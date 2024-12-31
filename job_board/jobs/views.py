# jobs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, JobPostForm, DefaultJobApplicationForm
from .models import Job, JobApplication, UserProfile
import json
from django.http import FileResponse

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                is_company=form.cleaned_data['is_company'],
                company_name=form.cleaned_data['company_name']
            )
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'jobs/register.html', {'form': form})

@login_required
def company_dashboard(request):
    if not request.user.userprofile.is_company:
        return redirect('seeker_dashboard')
    
    jobs = Job.objects.filter(company=request.user.userprofile)
    return render(request, 'jobs/company_dashboard.html', {'jobs': jobs})

@login_required
def seeker_dashboard(request):
    if request.user.userprofile.is_company:
        return redirect('company_dashboard')
    
    applied_jobs = JobApplication.objects.filter(applicant=request.user.userprofile)
    available_jobs = Job.objects.filter(is_active=True)
    
    return render(request, 'jobs/seeker_dashboard.html', {
        'applied_jobs': applied_jobs,
        'available_jobs': available_jobs
    })

@login_required
def post_job(request):
    if not request.user.userprofile.is_company:
        return redirect('home')
        
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user.userprofile
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('company_dashboard')
    else:
        form = JobPostForm()
    
    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def apply_job(request, job_id):
    if request.user.userprofile.is_company:
        return redirect('home')
        
    job = get_object_or_404(Job, pk=job_id)
    
    if JobApplication.objects.filter(job=job, applicant=request.user.userprofile).exists():
        messages.warning(request, 'You have already applied for this job!')
        return redirect('seeker_dashboard')
    
    if request.method == 'POST':
        if job.custom_form:
            custom_form = job.custom_form if isinstance(job.custom_form, list) else json.loads(job.custom_form)
            form_data = {field: request.POST.get(field) for field in custom_form}
        else:
            form = DefaultJobApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                application = JobApplication.objects.create(
                    job=job,
                    applicant=request.user.userprofile,
                    resume=request.FILES['resume'],
                    form_data={'cover_letter': form.cleaned_data['cover_letter']}
                )
                messages.success(request, 'Application submitted successfully!')
                return redirect('seeker_dashboard')
    
    if job.custom_form:
        custom_form = job.custom_form if isinstance(job.custom_form, list) else json.loads(job.custom_form)
        return render(request, 'jobs/apply_job.html', {
            'job': job,
            'custom_form': custom_form
        })
    else:
        form = DefaultJobApplicationForm()
        return render(request, 'jobs/apply_job.html', {
            'job': job,
            'form': form
        })
    
@login_required
def manage_application(request, application_id):
    if not request.user.userprofile.is_company:
        return redirect('home')
        
    application = get_object_or_404(JobApplication, pk=application_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['accepted', 'rejected']:
            application.status = status
            application.save()
            messages.success(request, f'Application {status} successfully!')
    
    return redirect('company_dashboard')

def job_detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})

@login_required
def view_resume(request, application_id):
    application = get_object_or_404(JobApplication, pk=application_id)
    if request.user.userprofile != application.job.company:
        return redirect('home')
    
    response = FileResponse(application.form_data['resume'])
    return response

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.user.userprofile != job.company:
        return redirect('home')
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
    return redirect('company_dashboard')