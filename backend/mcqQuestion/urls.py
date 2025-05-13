from django.urls import path
from . import views

urlpatterns = [
    path(
        'assessments/<str:assessment_id>/mcq-questions/',
        views.McqQuestionListCreateAPIView.as_view(),
        name='mcq-question-list-create'
    ),
    path(
        'mcq-questions/<str:pk>/',
        views.McqQuestionRetrieveUpdateDestroyAPIView.as_view(),
        name='mcq-question-detail'
    ),
    path(
        'assessments/<str:assessment_id>/generate-from-text/',
        views.GenerateMCQsFromTextView.as_view(),
        name='mcq-generate-from-text'
    ),
    path(
        'assessments/<str:assessment_id>/generate-from-pdf/',
        views.GenerateMCQsFromPDFView.as_view(),
        name='mcq-generate-from-pdf'
    ),
]
