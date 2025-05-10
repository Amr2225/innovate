from django.contrib import admin
from .models import CodingQuestion, TestCase

# Register your models here.
admin.site.register(CodingQuestion)
admin.site.register(TestCase)