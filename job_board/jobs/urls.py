# jobs/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.http import FileResponse
from . import views

urlpatterns = [
    path('', views.seeker_dashboard, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='jobs/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('seeker/dashboard/', views.seeker_dashboard, name='seeker_dashboard'),
    path('job/post/', views.post_job, name='post_job'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('application/<int:application_id>/manage/', views.manage_application, name='manage_application'),
    path('application/<int:application_id>/resume/', views.view_resume, name='view_resume'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
]
