from django.urls import path
from . import views

urlpatterns = [
    path('', views.PolicyUpdateOrCreateAPIView.as_view(), name='policy-list-update-create'),
]
