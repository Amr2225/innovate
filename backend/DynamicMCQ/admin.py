from django.contrib import admin
from .models import DynamicMCQ, DynamicMCQQuestions

admin.site.register(DynamicMCQ)
admin.site.register(DynamicMCQQuestions)
