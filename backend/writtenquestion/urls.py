from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HandwrittenQuestionViewSet, WrittenQuestionViewSet

router = DefaultRouter()
router.register(r'handwritten-questions', HandwrittenQuestionViewSet, basename='handwrittenquestion')
router.register(r'written-answers', WrittenQuestionViewSet, basename='writtenquestion')

urlpatterns = [
    path('', include(router.urls)),
]