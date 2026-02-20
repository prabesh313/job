from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, JobPost, Application


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[('candidate', 'I am looking for a job'), ('recruiter', 'I want to hire talent')])
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['skills', 'experience_level', 'years_experience', 'bio']
        widgets = {
            'skills': forms.TextInput(attrs={'placeholder': 'e.g. Python, Django, SQL, React'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell recruiters about yourself...'}),
        }
        help_texts = {
            'skills': 'Comma-separated list of your skills',
        }


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['company_name', 'company_description']
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = [
            'title', 'description', 'required_skills', 'nice_to_have_skills',
            'required_experience_level', 'min_years_experience',
            'location', 'salary_min', 'salary_max'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'required_skills': forms.TextInput(attrs={'placeholder': 'e.g. Python, Django, PostgreSQL'}),
            'nice_to_have_skills': forms.TextInput(attrs={'placeholder': 'e.g. Docker, Kubernetes'}),
        }
        help_texts = {
            'required_skills': 'Comma-separated skills candidates must have',
            'nice_to_have_skills': 'Comma-separated bonus skills',
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Tell the recruiter why you\'re the perfect fit...'
            })
        }
