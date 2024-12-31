from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
from django.template.loader import render_to_string
from .models import Course, TestResult, UserProfile
import os
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(pre_delete, sender=Course)
def delete_course_files(sender, instance, **kwargs):
    try:
        if instance.pdf_file:
            if os.path.isfile(instance.pdf_file.path):
                os.remove(instance.pdf_file.path)
            
        # Clean up any associated thumbnails or preview files
        preview_path = f"{os.path.splitext(instance.pdf_file.path)[0]}_preview.jpg"
        if os.path.exists(preview_path):
            os.remove(preview_path)
    except Exception as e:
        logger.error(f"Error deleting course files: {str(e)}")

@receiver(post_save, sender=TestResult)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            profile = instance.user.userprofile
            
            # Update user's test statistics
            profile.total_tests_taken = TestResult.objects.filter(user=instance.user).count()
            profile.average_score = TestResult.objects.filter(
                user=instance.user
            ).aggregate(Avg('score'))['score__avg'] or 0
            
            # Update achievement levels
            if instance.score == 5:
                profile.perfect_scores += 1
            
            # Calculate topic mastery
            topic_scores = TestResult.objects.filter(
                user=instance.user,
                topic=instance.topic
            ).aggregate(Avg('score'))['score__avg'] or 0
            
            if topic_scores >= 4.5:
                profile.mastered_topics.add(instance.topic)
            
            profile.save()
            
            # Send notification email
            if instance.score >= 4:
                context = {
                    'user': instance.user,
                    'score': instance.score,
                    'topic': instance.get_topic_display(),
                    'level': instance.get_level_display()
                }
                
                html_message = render_to_string('emails/test_success.html', context)
                
                send_mail(
                    subject='Congratulations on Your Test Result!',
                    message=f'You scored {instance.score}/5 on {instance.get_topic_display()}!',
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.user.email],
                    fail_silently=True
                )
            
            # Create achievement notifications
            if profile.perfect_scores in [1, 5, 10, 25, 50]:
                Notification.objects.create(
                    user=instance.user,
                    title='Achievement Unlocked!',
                    message=f'You have earned {profile.perfect_scores} perfect scores!'
                )
                
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")

@receiver(pre_save, sender=Course)
def validate_course_files(sender, instance, **kwargs):
    if instance.pdf_file:
        # Validate file size
        if instance.pdf_file.size > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("File size too large ( > 10MB )")
        
        # Validate file type
        allowed_types = ['application/pdf']
        file_type = magic.from_buffer(instance.pdf_file.read(), mime=True)
        if file_type not in allowed_types:
            raise ValueError("Invalid file type. Only PDF files are allowed.")

# Register signal for course completion tracking
@receiver(post_save, sender=TestResult)
def track_course_completion(sender, instance, created, **kwargs):
    if created:
        try:
            # Check if user has completed all levels for a topic
            levels_completed = TestResult.objects.filter(
                user=instance.user,
                topic=instance.topic,
                score__gte=4  # Consider a score of 4 or higher as completion
            ).values('level').distinct().count()
            
            if levels_completed == 3:  # All levels completed
                CourseCompletion.objects.create(
                    user=instance.user,
                    topic=instance.topic,
                    completion_date=timezone.now()
                )
                
                # Notify user of course completion
                Notification.objects.create(
                    user=instance.user,
                    title='Course Completed!',
                    message=f'Congratulations! You have mastered all levels of {instance.get_topic_display()}!'
                )
        except Exception as e:
            logger.error(f"Error tracking course completion: {str(e)}")