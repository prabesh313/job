# 🎯 TalentMatch — Django Job Portal

A points-based job portal where candidates are matched to jobs using a smart scoring engine.

---

## 🚀 Quick Start

```bash
# 1. Install Django
pip install -r requirements.txt

# 2. Run migrations
python manage.py makemigrations jobs
python manage.py migrate

# 3. Create an admin account (optional)
python manage.py createsuperuser

# 4. Start the server
python manage.py runserver
```

Then open: **http://127.0.0.1:8000**

---

## 🏗️ Project Structure

```
jobportal/
├── manage.py
├── requirements.txt
├── core/                   # Django project config
│   ├── settings.py
│   └── urls.py
└── jobs/                   # Main app
    ├── models.py           # UserProfile, JobPost, Application
    ├── views.py            # All page logic
    ├── forms.py            # Registration, job posting, application forms
    ├── scoring.py          # 🎯 Points scoring engine
    ├── urls.py
    └── templates/jobs/
        ├── base.html
        ├── home.html       # Job listings + search
        ├── job_detail.html # Job detail + match breakdown
        ├── apply.html      # Application form
        ├── register.html
        ├── login.html
        ├── edit_profile.html
        ├── post_job.html
        ├── my_applications.html
        └── recruiter_dashboard.html
```

---

## 🎯 Scoring System

| Factor | Points |
|--------|--------|
| Exact required skill match | +10 each |
| Partial required skill match | +5 each |
| Nice-to-have skill match | +5 each |
| Experience meets requirement | +20 |
| Experience significantly exceeds | +30 |
| Experience below requirement | +5 |

Candidates are ranked by total score on the recruiter dashboard.

---

## 👤 User Roles

### Candidate
- Register → complete profile with skills & years of experience
- Browse jobs with personal match scores shown
- Apply with a cover letter
- Track application status in "My Applications"

### Recruiter
- Register → set company name
- Post jobs with required/nice-to-have skills
- View applicants ranked by match score
- Update application status: Review → Shortlist → Hire / Reject

---

## 🛠️ Admin

Access `/admin/` after creating a superuser for full data management.
