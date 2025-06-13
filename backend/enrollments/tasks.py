from celery import shared_task

@shared_task
def promote_students_auto():
    # logic for promoting students based on institution settings
    print("Running automatic promotion task.")
