from django_celery_beat.models import PeriodicTask, CrontabSchedule
from json import dumps
from datetime import time
from users.models import User
from institution_policy.models import InstitutionPolicy

def create_promotion_task_for_institution(institution, promotion_time: time):
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=str(promotion_time.minute),
        hour=str(promotion_time.hour),
        day_of_week='*',
        day_of_month='*',
        month_of_year='*'
    )

    PeriodicTask.objects.update_or_create(
        name=f"promote_students_{institution.id}",
        defaults={
            "crontab": schedule,
            "task": "enrollments.tasks.promote_students_auto",
            "args": dumps([str(institution.id)])  # ← convert UUID to string
        }
    )


def schedule_all_promotions():
    policies = InstitutionPolicy.objects.filter(
        promotion_time__isnull=False
    )

    for policy in policies:
        create_promotion_task_for_institution(policy.institution, policy.promotion_time)