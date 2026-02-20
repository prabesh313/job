from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField


EXPERIENCE_LEVELS = [
    ('entry', 'Entry Level (0-2 years)'),
    ('mid', 'Mid Level (2-5 years)'),
    ('senior', 'Senior Level (5-10 years)'),
    ('lead', 'Lead / Principal (10+ years)'),
]

ROLE_CHOICES = [
    ('candidate', 'Candidate'),
    ('recruiter', 'Recruiter'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    # Candidate fields
    skills = models.TextField(blank=True, help_text="Comma-separated skills (e.g. Python, Django, SQL)")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    # Recruiter fields
    company_name = models.CharField(max_length=200, blank=True)
    company_description = models.TextField(blank=True)

    def get_skills_list(self):
        if not self.skills:
            return []
        return [s.strip().lower() for s in self.skills.split(',') if s.strip()]

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class JobPost(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_posts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField(help_text="Comma-separated required skills")
    nice_to_have_skills = models.TextField(blank=True, help_text="Comma-separated nice-to-have skills")
    required_experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='entry')
    min_years_experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=200, default='Remote')
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_required_skills_list(self):
        return [s.strip().lower() for s in self.required_skills.split(',') if s.strip()]

    def get_nice_skills_list(self):
        if not self.nice_to_have_skills:
            return []
        return [s.strip().lower() for s in self.nice_to_have_skills.split(',') if s.strip()]

    def __str__(self):
        return f"{self.title} @ {self.recruiter.profile.company_name or self.recruiter.username}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewed', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')

    # Points breakdown (stored for display)
    points_total = models.IntegerField(default=0)
    points_breakdown = JSONField(default=dict)

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'candidate')
        ordering = ['-points_total']

    def __str__(self):
        return f"{self.candidate.username} → {self.job.title} ({self.points_total} pts)"
