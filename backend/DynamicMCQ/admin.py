from django.contrib import admin
from .models import DynamicMCQ, DynamicMCQQuestions

# Register your models here.

admin.site.register(DynamicMCQ)
admin.site.register(DynamicMCQQuestions)
