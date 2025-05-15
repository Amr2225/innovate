from django.urls import path
from .views import (
    AssessmentListCreateAPIView,
    AssessmentDetailAPIView,
    AssessmentScoreListCreateAPIView,
    AssessmentScoreRetrieveUpdateDestroyAPIView,
    QuestionListCreateAPIView,
    QuestionResponseCreateAPIView,
    QuestionResponseUpdateAPIView,
    get_student_assessment_grade
)

urlpatterns = [
    # Assessment URLs
    path('', AssessmentListCreateAPIView.as_view(), name='assessment-list-create'),
    path('<uuid:pk>/', AssessmentDetailAPIView.as_view(), name='assessment-detail'),
    
    # Question URLs
    path('<uuid:assessment_id>/questions/', QuestionListCreateAPIView.as_view(), name='question-list-create'),
    
    # Question Response URLs
    path('responses/create/', QuestionResponseCreateAPIView.as_view(), name='question-response-create'),
    path('responses/<uuid:pk>/update/', QuestionResponseUpdateAPIView.as_view(), name='question-response-update'),
    
    # Assessment Score URLs
    path('scores/', AssessmentScoreListCreateAPIView.as_view(), name='assessment-score-list-create'),
    path('scores/<uuid:pk>/', AssessmentScoreRetrieveUpdateDestroyAPIView.as_view(), name='assessment-score-detail'),
    path('<uuid:assessment_id>/grade/', get_student_assessment_grade, name='student-assessment-grade'),
]
