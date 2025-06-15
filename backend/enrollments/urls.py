from django.urls import path
from . import views

urlpatterns = [
    path('', views.EligibleCoursesAPIView.as_view(), name='courses-eligible'),
    path('my-courses/', views.EnrolledCoursesAPIView.as_view(),
         name='my-enrolled-courses'),
    path('<uuid:enrollment_id>/assessment-scores/',
         views.EnrollmentAssessmentScoresView.as_view(), name='enrollment-assessment-scores'),
    path('<uuid:enrollment_id>/score/',
         views.EnrollmentScoreView.as_view(), name='enrollment-score'),
    path('<uuid:pk>/update-score/', views.EnrollmentUpdateScoreView.as_view(),
         name='enrollment-update-score'),
    path('promote-students/', views.PromoteStudentsAPIView.as_view(),
         name='promote-students'),
    path('promote-students-summer/', views.PromoteStudentsSummerAPIView.as_view(),
         name='promote-students-summer'),
    path('all-grades/', views.AllStudentGradesView.as_view(),
         name='all_student_grades')
]
