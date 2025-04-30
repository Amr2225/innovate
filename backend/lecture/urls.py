from django.urls import path
from . import views

urlpatterns = [
    path('', views.LectureListCreateAPIView.as_view()),
    path('<uuid:p_id>', views.LectureRetrieveUpdateDestroyAPIView.as_view()),
    path('progress', views.LecturesProgressListCreateAPIView.as_view()),
    path('<uuid:lecture_id>/progress', views.LectureProgressRetrieveAPIView.as_view()),
    path('chapter/<uuid:chapter_id>', views.ChapterLecturesAPIView.as_view(), name='chapter-lectures'),
]
