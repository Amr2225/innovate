from django.apps import AppConfig


class EnrollmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'enrollments'
    verbose_name = 'Enrollments'

    def ready(self):
        import enrollments.signals  # Import signals when app is ready
