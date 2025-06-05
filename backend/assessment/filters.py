from django_filters import rest_framework as filters
from .models import Assessment
from mcqQuestion.models import McqQuestion
from HandwrittenQuestion.models import HandwrittenQuestion
from DynamicMCQ.models import DynamicMCQ, DynamicMCQQuestions 