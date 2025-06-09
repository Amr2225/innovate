from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HandwrittenQuestionViewSet,
    HandwrittenQuestionScoreViewSet,
    ExtractTextFromImageAPIView,
    ExtractAndEvaluateAnswerAPIView
)

router = DefaultRouter()
router.register(r'questions', HandwrittenQuestionViewSet,
                basename='handwritten-question')
router.register(r'scores', HandwrittenQuestionScoreViewSet,
                basename='handwritten-score')

urlpatterns = [
    path('', include(router.urls)),
    # path('extract-text/', ExtractTextFromImageAPIView.as_view(), name='extract-text'),
    # path('extract-and-evaluate/', ExtractAndEvaluateAnswerAPIView.as_view(), name='extract-and-evaluate'),
]
