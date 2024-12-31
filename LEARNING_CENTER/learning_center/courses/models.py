from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class Course(models.Model):
    TOPICS = (
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
    )
    
    DIFFICULTIES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    topic = models.CharField(max_length=50, choices=TOPICS)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTIES, default='beginner')
    video_url = models.URLField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='course_pdfs/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_courses')
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return f'/course/{self.slug}/'
        
    @property
    def enrolled_count(self):
        return self.students.count()

class Topic(models.Model):
    """Model to manage course topics and their hierarchical relationships"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subtopics')
    order = models.PositiveIntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.name

class Question(models.Model):
    LEVELS = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    topic = models.CharField(max_length=50, choices=Course.TOPICS)
    level = models.CharField(max_length=20, choices=LEVELS)
    question_text = models.TextField()
    explanation = models.TextField(blank=True, help_text="Explanation of the correct answer")
    option_1 = models.CharField(max_length=200)
    option_2 = models.CharField(max_length=200)
    option_3 = models.CharField(max_length=200)
    option_4 = models.CharField(max_length=200)
    correct_answer = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['topic', 'level']
    
    def __str__(self):
        return f"{self.topic} - {self.level} - {self.question_text[:50]}"

class TestResult(models.Model):
    LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVELS, default='beginner')  # Changed from integer to CharField
    score = models.DecimalField(max_digits=5, decimal_places=2)
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

    
    def __str__(self):
        return f"{self.user.username} - {self.topic} - {self.level} - {self.score}/{self.total_questions}"
    
    @property
    def score_percentage(self):
        return (self.score / self.total_questions) * 100

class QuestionResponse(models.Model):
    """Model to track individual question responses in a test"""
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.IntegerField(null=True)
    is_correct = models.BooleanField()
    time_spent = models.DurationField(null=True, blank=True)
    
    class Meta:
        unique_together = ['test_result', 'question']

class UserProgress(models.Model):
    """Model to track overall user progress"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    courses_completed = models.ManyToManyField(Course, related_name='completions')
    total_study_time = models.DurationField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Progress for {self.user.username}"

class CourseProgress(models.Model):
    """Model to track user progress in specific courses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topics_completed = models.ManyToManyField(Topic)
    last_accessed = models.DateTimeField(auto_now=True)
    progress_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    
    class Meta:
        unique_together = ['user', 'course']
        
    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.progress_percentage}%"
    
class CourseVideo(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_id = models.CharField(max_length=20)
    thumbnail_url = models.URLField()
    duration = models.CharField(max_length=10)
    channel_name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def embed_url(self):
        return f"https://www.youtube.com/embed/{self.video_id}"
