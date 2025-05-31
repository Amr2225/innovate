from django.urls import path
from .views import (
    DynamicMCQListCreateAPIView,
    DynamicMCQDetailAPIView,
    DynamicMCQQuestionsListCreateAPIView,
    DynamicMCQQuestionsDetailAPIView
)

urlpatterns = [
    path('', DynamicMCQListCreateAPIView.as_view(), name='dynamic-mcq-list-create'),
    path('<uuid:pk>/', DynamicMCQDetailAPIView.as_view(), name='dynamic-mcq-detail'),
    path('<uuid:dynamic_mcq_id>/questions/', DynamicMCQQuestionsListCreateAPIView.as_view(), name='dynamic-mcq-questions-list-create'),
    path('<uuid:dynamic_mcq_id>/questions/<uuid:pk>/', DynamicMCQQuestionsDetailAPIView.as_view(), name='dynamic-mcq-questions-detail'),
] 