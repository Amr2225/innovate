from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.http import HttpResponse


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('user.urls')),
    path('courses/', include('courses.urls')),
    path('institution/', include('institution.urls')),

    # Authentication-related
    # path('accounts/', include('allauth.urls')),

    # User API
    # path("api/user/", include("user.urls")),

    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
