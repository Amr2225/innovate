from django.contrib import admin
from django.urls import path

from users import verificatonViews, institutionViews, views
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
    path('verify-email/<str:token>/',
<<<<<<< HEAD
         verificatonViews.VerifyEmailView.as_view(), name="verify_email"),

    path('resend-verification-email/', verificatonViews.ResendVerificationEmailView.as_view(),
         name="resend-verification-email"),

    path('resend-verification-email/<str:token>/', verificatonViews.ResendVerificationEmailView.as_view(),
         name="resend-verification-email-with-token"),

    # Institution
    path('institution/register/', institutionViews.InstitutionRegisterView.as_view(),
         name="institution_register"),
    path('institution/users/',
         institutionViews.InstitutionUserView.as_view(), name="institution_register_user"),
    path('institution/users/register/csv/',
         institutionViews.BulkUserImportView.as_view(), name="institution_register_user"),
=======
         views.VerifyEmailView.as_view(), name="verify_email"),
    path('resend-verification-email/', views.ResendVerificationEmailView.as_view(),
         name="resend-verification-email"),
    path('resend-verification-email/<str:token>/', views.ResendVerificationEmailView.as_view(),
         name="resend-verification-email-with-token"),

    # Institution
    path('institution/register/', views.InstitutionRegisterView.as_view(),
         name="institution_register"),
    path('institution/users/',
         views.InstitutionUserView.as_view(), name="institution_register_user"),
    path('institution/users/register/csv/',
         views.BulkUserImportView.as_view(), name="institution_register_user"),
>>>>>>> c18b18b6528a743c9eafe47cb0522e151360994c
    path('add-credentials/', views.UserAddCredentialsView.as_view(), name="add_creds"),
]
