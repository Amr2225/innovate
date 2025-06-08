from django.urls import path
from .views import (
    AssessmentListCreateAPIView,
    AssessmentDetailAPIView,
    AssessmentScoreListCreateAPIView,
    AssessmentScoreDetailAPIView,
    AssessmentQuestionsAPIView,
    StudentGradesAPIView,
    AssessmentAllQuestionsAPIView,
    AssessmentStudentQuestionsAPIView,
)

urlpatterns = [
    # Assessment endpoints
    path('', AssessmentListCreateAPIView.as_view(),
         name='assessment-list-create'),
    path('<uuid:course_id>/', AssessmentListCreateAPIView.as_view(),
         name='course-assessments'),
    path('<uuid:pk>/', AssessmentDetailAPIView.as_view(), name='assessment-detail'),
    path('<uuid:pk>/questions/', AssessmentQuestionsAPIView.as_view(),
         name='assessment-questions'),
    path('<uuid:pk>/all-questions/', AssessmentAllQuestionsAPIView.as_view(),
         name='assessment-all-questions'),
    path('<uuid:pk>/student-questions/', AssessmentStudentQuestionsAPIView.as_view(),
         name='assessment-student-questions'),

    # AssessmentScore endpoints
    path('scores/', AssessmentScoreListCreateAPIView.as_view(),
         name='assessment-score-list-create'),
    path('scores/<uuid:pk>/', AssessmentScoreDetailAPIView.as_view(),
         name='assessment-score-detail'),

    # Student grades endpoint
    path('student-grades/<uuid:pk>/',
         StudentGradesAPIView.as_view(), name='student-grades'),
]
