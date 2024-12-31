# jobs/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_company = models.BooleanField(default=False)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class Job(models.Model):
    company = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    posted_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    custom_form = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    form_data = models.JSONField()
    status = models.CharField(max_length=20, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('job', 'applicant')
