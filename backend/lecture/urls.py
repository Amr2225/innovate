from django.urls import path
from . import views

urlpatterns = [
    path('', views.LectureListCreateAPIView.as_view()),
    path('<uuid:p_id>', views.LectureRetrieveUpdateDestroyAPIView.as_view()),
    path('progress', views.LecturesProgressListCreateAPIView.as_view()),
]
