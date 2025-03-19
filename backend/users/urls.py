from django.contrib import admin
from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # Auth
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('institution/register/', views.InstitutionRegisterView.as_view(),
         name="institution_register"),

    # Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Email Verification
    path('verify-email/', views.VerifyEmailView.as_view(), name="verify_email"),
    path('resend-verification-email/', views.ResendVerificationEmailView.as_view(),
         name="resend-verfication-email"),

]
