from django.urls import path, include
from .views import (
    userListView,
    RegisterView,
    VerifyEmailView,
    ResendVerificationCodeView,
    GoogleLoginView,
    GoogleAuthView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("users/", userListView.as_view(), name="get_users"),

    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationCodeView.as_view(),
         name='resend_verification'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Google authentication
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', GoogleAuthView.as_view(), name='google_callback'),

    # dj-rest-auth endpoints
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls')),
]
