from django.contrib import admin
from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # Auth
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path("login-access/", views.LoginAccessView.as_view(), name="first_login"),

    # Google Auth
    path("google-auth/", views.GoogleAuthView.as_view(), name="google_auth"),

    # Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Email Verification
    path('verify-email/', views.VerifyEmailView.as_view(), name="verify_email"),
    path('resend-verification-email/', views.ResendVerificationEmailView.as_view(),
         name="resend-verfication-email"),

    # Institution
    path('institution/register/', views.InstitutionRegisterView.as_view(),
         name="institution_register"),
    path('institution/users/register/',
         views.InstitutionRegisterUserView.as_view(), name="institution_register_user"),
    path('institution/users/register/csv/',
         views.BulkUserImportView.as_view(), name="institution_register_user"),
    path('add-credentials/', views.UserAddCredentialsView.as_view(), name="add_creds"),
]
