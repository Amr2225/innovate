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
from .sse import MyView, TempUploadImage

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

    # USED
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

    # SSE
    path('sse/<str:token>/<uuid:assessment_id>/<uuid:question_id>/',
         MyView.as_view(), name='sse'),
    path('temp-handwritten-image/<uuid:assessment_id>/<uuid:question_id>/',
         TempUploadImage.as_view(), name='temp-upload-image'),
]
