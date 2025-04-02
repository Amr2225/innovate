from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('courses/', include('courses.urls')),
    # Auth API
    path("auth/", include("users.urls")),

    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Rest Framework
    path("api-auth/", include("rest_framework.urls")),
]
