"""
Job Portal Setup Script
Run: python setup.py
Then: cd jobportal_project && python manage.py runserver
"""
import os, subprocess, sys

def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
    return result.stdout

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.join(BASE, "jobportal_project")

print("📦 Installing Django...")
run(f"{sys.executable} -m pip install django --quiet")

print("🏗️  Creating Django project...")
run(f"django-admin startproject core .", cwd=PROJECT) if os.path.exists(PROJECT) else None
os.makedirs(PROJECT, exist_ok=True)
run(f"django-admin startproject core .", cwd=PROJECT)
run(f"{sys.executable} manage.py startapp jobs", cwd=os.path.join(PROJECT))

print("✅ Project scaffolded. Now writing files...")
