from django.urls import path
from .views import userListView

urlpatterns = [
    path("", userListView.as_view(), name="get_users")
]
