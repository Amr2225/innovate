from django.urls import path
from . import views

urlpatterns = [
    path('', views.EligibleCoursesAPIView.as_view(), name='courses-eligible'),
    path('my-courses/', views.EnrolledCoursesAPIView.as_view(),
         name='my-enrolled-courses'),
]
