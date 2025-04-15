from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListCreateAPIView.as_view()),
    path('<uuid:p_id>', views.RetrieveUpdateDestroyCourseDetailAPIView.as_view()),
    path('institution/<uuid:institution_id>/courses/', views.CoursesByInstitutionAPIView.as_view(), name='courses-by-institution'),
]
