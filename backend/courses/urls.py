from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListCreateAPIView.as_view()),
    path('<uuid:p_id>', views.RetrieveUpdateDestroyCourseDetailAPIView.as_view()),
    path('<uuid:course_id>/progress/', views.CourseProgressListAPIView.as_view()),
    path('import/csv/', views.BulkCourseImportView.as_view()),
]
