from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChapterListCreateAPIView.as_view(), name='chapter-list-create'),
    path('<uuid:p_id>', views.ChapterRetrieveUpdateDestroyAPIView.as_view(), name='chapter-detail'),
    path('course/<uuid:course_id>', views.CourseChaptersAPIView.as_view(), name='course-chapters'),
]
