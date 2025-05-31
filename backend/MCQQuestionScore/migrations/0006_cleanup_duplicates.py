from django.db import migrations
from django.contrib.contenttypes.models import ContentType
from mcqQuestion.models import McqQuestion
from DynamicMCQ.models import DynamicMCQQuestions

def cleanup_duplicates(apps, schema_editor):
    MCQQuestionScore = apps.get_model('MCQQuestionScore', 'MCQQuestionScore')
    db_alias = schema_editor.connection.alias

    # Get content types
    mcq_content_type = ContentType.objects.get_for_model(McqQuestion)
    dynamic_mcq_content_type = ContentType.objects.get_for_model(DynamicMCQQuestions)

    # Group by content_type, object_id, and enrollment
    seen = set()
    duplicates = []

    for score in MCQQuestionScore.objects.using(db_alias).all():
        key = (score.content_type_id, score.object_id, score.enrollment_id)
        if key in seen:
            duplicates.append(score.id)
        else:
            seen.add(key)

    # Delete duplicates
    if duplicates:
        MCQQuestionScore.objects.using(db_alias).filter(id__in=duplicates).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('MCQQuestionScore', '0006_remove_mcqquestionscore_mcqquestion_questio_1dfddc_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(cleanup_duplicates),
    ] 