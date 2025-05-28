from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    McqQuestionViewSet,
    McqQuestionListCreateAPIView,
    McqQuestionRetrieveUpdateDestroyAPIView,
    GenerateMCQsFromTextView,
    GenerateMCQsFromPDFView
)

router = DefaultRouter()
router.register(r'mcq-questions', McqQuestionViewSet, basename='mcq-question')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'assessments/<str:assessment_id>/mcq-questions/',
        McqQuestionListCreateAPIView.as_view(),
        name='mcq-question-list-create'
    ),
    path(
        'mcq-questions/<str:pk>/',
        McqQuestionRetrieveUpdateDestroyAPIView.as_view(),
        name='mcq-question-detail'
    ),
    path(
        'assessments/<str:assessment_id>/generate-from-text/',
        GenerateMCQsFromTextView.as_view(),
        name='mcq-generate-from-text'
    ),
    path(
        'assessments/<str:assessment_id>/generate-from-pdf/',
        GenerateMCQsFromPDFView.as_view(),
        name='mcq-generate-from-pdf'
    ),
]
