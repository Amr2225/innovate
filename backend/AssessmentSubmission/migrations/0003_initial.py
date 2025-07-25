# Generated by Django 5.1.3 on 2025-06-14 03:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('AssessmentSubmission', '0002_initial'),
        ('enrollments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmentsubmission',
            name='enrollment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='assessment_submissions', to='enrollments.enrollments'),
        ),
        migrations.AlterUniqueTogether(
            name='assessmentsubmission',
            unique_together={('assessment', 'enrollment')},
        ),
    ]
