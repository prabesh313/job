from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('jobs/<int:pk>/delete/', views.delete_job, name='delete_job'), 
    path('my-applications/', views.my_applications, name='my_applications'),
    path('post-job/', views.post_job, name='post_job'),
    path('recruiter/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('applications/<int:app_id>/status/<str:status>/', views.update_application_status, name='update_status'),
    path('choose-role/', views.choose_role, name='choose_role'),
       
]
