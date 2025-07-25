# Generated by Django 5.1.3 on 2025-06-14 03:15

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentSubmission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4,
                 editable=False, primary_key=True, serialize=False)),
                ('mcq_answers', models.JSONField(default=dict,
                 help_text='Dictionary of question_id: selected_answer')),
                ('handwritten_answers', models.JSONField(default=dict,
                 help_text='Dictionary of question_id: image_path')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('is_submitted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
    ]
