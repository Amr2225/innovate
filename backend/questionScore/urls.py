from django.urls import path
from .views import QuestionScoreListCreateAPIView, QuestionScoreDetailAPIView

urlpatterns = [
    path('', QuestionScoreListCreateAPIView.as_view(), name='question-score-list-create'),
    path('<uuid:pk>/', QuestionScoreDetailAPIView.as_view(), name='question-score-detail'),
] 