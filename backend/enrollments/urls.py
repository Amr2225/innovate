from django.urls import path
from . import views

urlpatterns = [
    path('enroll', views.EligibleCoursesAPIView.as_view(), name='courses-eligible'),
    path('my-courses', views.EnrolledCoursesAPIView.as_view(), name='my-enrolled-courses'),
    path('enrollments/<uuid:enrollment_id>/assessment-scores/', views.EnrollmentAssessmentScoresView.as_view(), name='enrollment-assessment-scores'),
    path('enrollments/<uuid:enrollment_id>/score/', views.EnrollmentScoreView.as_view(), name='enrollment-score'),
    path('enrollments/<uuid:pk>/update-score/', views.EnrollmentUpdateScoreView.as_view(), name='enrollment-update-score'),
]
