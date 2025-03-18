from django.urls import path
from . import views

urlpatterns = [
    path('', views.InstitutionListCreateAPIView.as_view()),
    path('<str:p_id>', views.RetrieveUpdateDestroyInstitutionDetailAPIView.as_view())
]
