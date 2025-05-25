from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('courses/', include('courses.urls')),
    path('enrollments/', include('enrollments.urls')),
    path('chapter/', include('chapter.urls')),
    path('lecture/', include('lecture.urls')),
    path('assessment/', include('assessment.urls')),
    path('mcqQuestion/', include('mcqQuestion.urls')), 
    path('chat/', include('chat.urls')), 
    path('mcqQuestionScore/', include('MCQQuestionScore.urls')), 
    path('handwrittenQuestion/', include('HandwrittenQuestion.urls')),
    path('codingQuestion/', include('CodingQuestion.urls')),
    path('dynamicMCQ/', include('DynamicMCQ.urls')),
    path('assessmentSubmission/', include('AssessmentSubmission.urls')),


    # Auth API
    path("auth/", include("users.urls")),

    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Rest Framework
    path("api-auth/", include("rest_framework.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)