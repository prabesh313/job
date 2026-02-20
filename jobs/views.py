from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import UserProfile, JobPost, Application
from .forms import RegisterForm, CandidateProfileForm, RecruiterProfileForm, JobPostForm, ApplicationForm
from .scoring import calculate_score


# ──────────────────────────────────────────────
#  Auth & Registration
# ──────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            UserProfile.objects.create(user=user, role=role)
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Complete your profile to get started.')
            return redirect('edit_profile')
    else:
        form = RegisterForm()
    return render(request, 'jobs/register.html', {'form': form})


# ──────────────────────────────────────────────
#  Home / Job Listings
# ──────────────────────────────────────────────

def home(request):
    jobs = JobPost.objects.filter(is_active=True).order_by('-created_at')
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    exp = request.GET.get('exp', '')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__icontains=query)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if exp:
        jobs = jobs.filter(required_experience_level=exp)

    # If candidate is logged in, show their match scores
    scored_jobs = []
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'candidate':
        profile = request.user.profile
        applied_ids = set(Application.objects.filter(candidate=request.user).values_list('job_id', flat=True))
        for job in jobs:
            score = calculate_score(profile, job)
            scored_jobs.append({
                'job': job,
                'score': score,
                'already_applied': job.id in applied_ids,
            })
        scored_jobs.sort(key=lambda x: x['score']['total'], reverse=True)
    else:
        scored_jobs = [{'job': j, 'score': None, 'already_applied': False} for j in jobs]

    return render(request, 'jobs/home.html', {
        'scored_jobs': scored_jobs,
        'query': query,
        'location': location,
        'exp': exp,
    })


# ──────────────────────────────────────────────
#  Job Detail & Apply
# ──────────────────────────────────────────────

def job_detail(request, pk):
    job = get_object_or_404(JobPost, pk=pk, is_active=True)
    score = None
    already_applied = False

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.role == 'candidate':
            score = calculate_score(request.user.profile, job)
            already_applied = Application.objects.filter(job=job, candidate=request.user).exists()

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'score': score,
        'already_applied': already_applied,
    })


@login_required
def apply_job(request, pk):
    job = get_object_or_404(JobPost, pk=pk, is_active=True)

    if request.user.profile.role != 'candidate':
        messages.error(request, 'Only candidates can apply for jobs.')
        return redirect('job_detail', pk=pk)

    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            score_data = calculate_score(request.user.profile, job)
            app = form.save(commit=False)
            app.job = job
            app.candidate = request.user
            app.points_total = score_data['total']
            app.points_breakdown = score_data['breakdown']
            app.save()
            messages.success(request, f'Application submitted! Your match score: {score_data["total"]} points.')
            return redirect('my_applications')
    else:
        form = ApplicationForm()

    score = calculate_score(request.user.profile, job)
    return render(request, 'jobs/apply.html', {'job': job, 'form': form, 'score': score})


# ──────────────────────────────────────────────
#  Profile
# ──────────────────────────────────────────────

@login_required
def edit_profile(request):
    profile = request.user.profile
    FormClass = CandidateProfileForm if profile.role == 'candidate' else RecruiterProfileForm

    if request.method == 'POST':
        form = FormClass(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('home')
    else:
        form = FormClass(instance=profile)

    return render(request, 'jobs/edit_profile.html', {'form': form, 'profile': profile})


# ──────────────────────────────────────────────
#  Candidate: My Applications
# ──────────────────────────────────────────────

@login_required
def my_applications(request):
    if request.user.profile.role != 'candidate':
        return redirect('home')
    apps = Application.objects.filter(candidate=request.user).select_related('job').order_by('-applied_at')
    return render(request, 'jobs/my_applications.html', {'applications': apps})


# ──────────────────────────────────────────────
#  Recruiter: Post & Manage Jobs
# ──────────────────────────────────────────────

@login_required
def post_job(request):
    if request.user.profile.role != 'recruiter':
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('home')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('recruiter_dashboard')
    else:
        form = JobPostForm()

    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def recruiter_dashboard(request):
    if request.user.profile.role != 'recruiter':
        return redirect('home')

    jobs = JobPost.objects.filter(recruiter=request.user).order_by('-created_at')
    job_data = []
    for job in jobs:
        apps = Application.objects.filter(job=job).select_related('candidate__profile').order_by('-points_total')
        job_data.append({'job': job, 'applications': apps, 'count': apps.count()})

    return render(request, 'jobs/recruiter_dashboard.html', {'job_data': job_data})


@login_required
def update_application_status(request, app_id, status):
    app = get_object_or_404(Application, pk=app_id, job__recruiter=request.user)
    valid_statuses = ['applied', 'reviewed', 'shortlisted', 'rejected', 'hired']
    if status in valid_statuses:
        app.status = status
        app.save()
        messages.success(request, f'Status updated to "{status}".')
    return redirect('recruiter_dashboard')



@login_required
def delete_job(request, pk):  
    job = get_object_or_404(JobPost, pk=pk, recruiter=request.user)
    if request.method == "POST":
        job.delete() 
        messages.success(request, "Job deleted successfully.")
    return redirect("recruiter_dashboard")

