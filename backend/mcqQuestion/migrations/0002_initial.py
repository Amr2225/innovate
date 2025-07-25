# Generated by Django 5.1.3 on 2025-06-14 03:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mcqQuestion', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='mcqquestion',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='mcq_questions_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='mcqquestion',
            index=models.Index(fields=['assessment'],
                               name='mcqQuestion_assessm_68dd1d_idx'),
        ),
        migrations.AddIndex(
            model_name='mcqquestion',
            index=models.Index(fields=['created_by'],
                               name='mcqQuestion_created_221ed9_idx'),
        ),
    ]
