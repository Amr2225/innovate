from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import os
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", default=0)

SITE_ID = 1

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

WEBSITE_URL = "http://localhost:8000"

AUTH_USER_MODEL = "users.User"


# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
]

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

# Google OAuth2
GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID', "")

INSTALLED_APPS = [
    # Django Core Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Rest Framework
    'rest_framework',
    'rest_framework_simplejwt',

    # Third-Party Apps
    "django_extensions",
    "django_filters",
    "nanoid_field",
    "drf_spectacular",
    'channels',
    'corsheaders',

    # Apps
    'users',
    'institution',
    "courses",
    'enrollments',
    'chapter',
    'lecture',
    'assessment',
    'mcqQuestion',
    'chat',
    'MCQQuestionScore',
    'HandwrittenQuestion',
    'DynamicMCQ',
    'AssessmentSubmission',
    'Code_Questions',
]

ASGI_APPLICATION = 'main.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    # TODO: will be removed in production
    # 'users.middleware.CustomExceptionMiddleware',
]

# To enable non active users to authenticate
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': os.environ.get("SQL_ENGINE"),
        'NAME': os.environ.get("SQL_DATABASE"),
        'USER': os.environ.get("SQL_USER"),
        'PASSWORD': os.environ.get("SQL_PASSWORD"),
        'HOST': os.environ.get("SQL_HOST"),
        'PORT': os.environ.get("SQL_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, "uploads")
MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, "uploads")
# Assessment Uploads Configuration
ASSESSMENT_UPLOADS_DIR = 'AssessmentUploads'
ASSESSMENT_UPLOADS_PATH = os.path.join(MEDIA_ROOT, ASSESSMENT_UPLOADS_DIR)

# Create upload directories if they don't exist
os.makedirs(ASSESSMENT_UPLOADS_PATH, exist_ok=True)
>>>>>>>>> Temporary merge branch 2

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # For Browsable API
    ),
    "DEFAULT_PERMISSIONS_CLASSES": (
        "rest_framework.permissions.IsAuthenticated"
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'institution.pagination.Pagination',
    # 'PAGE_SIZE': 10,
    # 'PAGE_SIZE_QUERY_PARAM': 'page_size',
    # TODO: Enable this in production
    # 'DEFAULT_RENDERER_CLASSES': [
    #     'rest_framework.renderers.JSONRenderer',
    # ],
}


# Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=60*3),
    "SIGNING_KEY": os.environ.get('JWT_MAIN', SECRET_KEY),
    "ISSUER": None,
    "USER_ID_FIELD": "id",  # The id field in the model
    "USER_ID_CLAIM": "user_id",
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'Innovate APIs',
    'DESCRIPTION': 'Innovate Backend APIs',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    "deepLinking": True,
    "SWAGGER_UI_DIST": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest",  # default
    # OTHER SETTINGS
    # 'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    # None will default to DRF's AUTHENTICATION_CLASSES
    # 'SERVE_AUTHENTICATION': None,
    # "SWAGGER_UI_FAVICON_HREF": settings.STATIC_URL + "your_company_favicon.png", # default is swagger favicon
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email Config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Payment Config
PAYMOB_PK = os.environ.get('PAYMOB_PK')
PAYMOB_SK = os.environ.get('PAYMOB_SK')
CLIENT_URL = os.environ.get('CLIENT_URL')

# AI CONFIG
AI_API_KEY = os.environ.get('AI_API_KEY')
AI_PROVIDER = os.environ.get('AI_PROVIDER')
AI_MODEL = os.environ.get('AI_MODEL')
CODER_AI_MODEL = os.environ.get('CODER_AI_MODEL')
