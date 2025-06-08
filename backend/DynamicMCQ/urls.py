from django.urls import path
from .views import (
    DynamicMCQListCreateAPIView,
    DynamicMCQDetailAPIView,
    DynamicMCQQuestionsListCreateAPIView,
    DynamicMCQQuestionsDetailAPIView
)

urlpatterns = [
    path('assessments/<uuid:assessment_id>/', DynamicMCQListCreateAPIView.as_view(), name='dynamic-mcq-list-create'),
    path('assessments/<uuid:assessment_id>/<uuid:pk>/', DynamicMCQDetailAPIView.as_view(), name='dynamic-mcq-detail'),
    path('assessments/<uuid:assessment_id>/<uuid:dynamic_mcq_id>/questions/', DynamicMCQQuestionsListCreateAPIView.as_view(), name='dynamic-mcq-questions-list-create'),
    path('assessments/<uuid:assessment_id>/<uuid:dynamic_mcq_id>/questions/<uuid:pk>/', DynamicMCQQuestionsDetailAPIView.as_view(), name='dynamic-mcq-questions-detail'),
] 