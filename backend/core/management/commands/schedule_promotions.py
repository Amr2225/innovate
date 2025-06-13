from django.core.management.base import BaseCommand
from enrollments.scheduler import schedule_all_promotions

class Command(BaseCommand):
    help = 'Create scheduled promotion tasks for institutions'

    def handle(self, *args, **kwargs):
        schedule_all_promotions()
        self.stdout.write("Scheduled all promotion tasks.")
