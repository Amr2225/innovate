from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListCreateAPIView.as_view()),
    path('<int:p_id>', views.RetrieveUpdateDestroyCourseDetailAPIView.as_view())
]
