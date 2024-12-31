from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Course related
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/load-more-videos/', views.load_more_videos, name='load_more_videos'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/create/', views.create_course, name='create_course'),
    path('course/<int:course_id>/edit/', views.edit_course, name='edit_course'),

    # Course videos
    path('course/<int:course_id>/videos/', views.manage_course_videos, name='manage_course_videos'),
    path('video/<int:video_id>/delete/', views.delete_course_video, name='delete_course_video'),

    # Tests and progress
    #path('tests/', views.test_list, name='test_list'),
    # Reordered test paths to handle more specific routes first
    #path('test/<str:topic>/<str:level>/submit/', views.submit_test, name='submit_test'),
    #path('test/<str:topic>/<str:level>/', views.take_test, name='take_test'),
    #path('test/result/<int:result_id>/', views.test_result, name='test_result'),
    #path('test/<str:topic>/', views.test_view, name='test'),
    path('tests/', views.test_list, name='test_list'),
path('test/<str:topic>/<str:difficulty>/submit/', views.submit_test, name='submit_test'),
path('test/result/<int:test_id>/', views.test_result, name='test_result'),
    # Progress tracking
    path('progress/', views.user_progress, name='user_progress'),
    path('topic/<int:topic_id>/progress/', views.topic_progress, name='topic_progress'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='courses/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]