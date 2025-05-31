from django.contrib import admin
from .models import HandwrittenQuestion, HandwrittenQuestionScore


# Register your models here.
admin.site.register(HandwrittenQuestion)
admin.site.register(HandwrittenQuestionScore)
