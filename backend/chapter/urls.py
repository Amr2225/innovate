from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChapterListCreateAPIView.as_view(), name='chapter-list-create'),
    path('<uuid:p_id>', views.ChapterRetrieveUpdateDestroyAPIView.as_view(), name='chapter-detail'),
]
