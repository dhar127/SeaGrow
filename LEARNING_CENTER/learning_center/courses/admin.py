# courses/admin.py
from django.contrib import admin
from .models import Course, Question, TestResult

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'author', 'created_at')
    list_filter = ('topic', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'topic', 'level')
    list_filter = ('topic', 'level')
    search_fields = ('question_text',)

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'level', 'score', 'completed_at')
    list_filter = ('topic', 'level')
    date_hierarchy = 'completed_at'