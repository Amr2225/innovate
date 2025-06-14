from django.urls import path

from users import verificatonViews, views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # Auth
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path("login-access/", views.LoginAccessView.as_view(), name="first_login"),
    path('add-credentials/', views.UserAddCredentialsView.as_view(), name="add_creds"),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(),
         name='token_refresh'),


    path('user/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('user/change-password/', views.ChangePasswordView.as_view(),
         name='change_password'),


    # Google Auth TODO: Implement this
    path("google-auth/", views.GoogleAuthView.as_view(), name="google_auth"),

    # Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Email Verification
    path('verify-email/<str:token>/',
         verificatonViews.VerifyEmailView.as_view(), name="verify_email"),

    path('resend-verification-email/', verificatonViews.ResendVerificationEmailView.as_view(),
         name="resend-verification-email"),

    path('resend-verification-email/<str:token>/', verificatonViews.ResendVerificationEmailView.as_view(),
         name="resend-verification-email-with-token"),

    path('institution-resend-verification-email/', verificatonViews.InstitutionResendVerificationEmailView.as_view(),
         name="institution-resend-verification-email"),

    path("institution-verify-email/", verificatonViews.InstitutionVerifyEmail.as_view(),
         name="institution-verify-email"),

    path("institution-verify-email/<str:email>/", verificatonViews.InstitutionVerifyEmail.as_view(),
         name="institution-verify-email-with-email"),

    # Institution
    path('institution/register/', views.InstitutionRegisterView.as_view(),
         name="institution_register"),
    path('institution/users/',
         views.InstitutionUserView.as_view(), name="institution_register_user"),
    path('institution/users/register/csv/',
         views.BulkUserImportView.as_view(), name="institution_register_user"),
    path('add-credentials/', views.UserAddCredentialsView.as_view(), name="add_creds"),
]
