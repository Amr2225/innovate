from django.urls import path
from .views import MCQQuestionScoreListCreateView, MCQQuestionScoreDetailView

urlpatterns = [
    path('mcq-scores/', MCQQuestionScoreListCreateView.as_view(), name='mcq-score-list-create'),
    path('mcq-scores/<str:pk>/', MCQQuestionScoreDetailView.as_view(), name='mcq-score-detail'),
] 