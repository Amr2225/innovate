from django_filters import rest_framework as filters
from .models import Assessment
from mcqQuestion.models import McqQuestion
from HandwrittenQuestion.models import HandwrittenQuestion
from DynamicMCQ.models import DynamicMCQ, DynamicMCQQuestions
from enrollments.models import Enrollments
from AssessmentSubmission.models import AssessmentSubmission


class AssessmentFilterSet(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    due_date = filters.DateTimeFilter()
    due_date_after = filters.DateTimeFilter(
        field_name='due_date', lookup_expr='gte')
    due_date_before = filters.DateTimeFilter(
        field_name='due_date', lookup_expr='lte')
    created_at = filters.DateTimeFilter()
    created_at_after = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte')

    has_submitted = filters.BooleanFilter(method='filter_has_submitted')

    def filter_has_submitted(self, queryset, name, value):
        request = self.request
        if not request or not request.user.is_authenticated:
            return queryset

        try:
            # Get the enrollment for the current user and assessment's course
            enrollments = Enrollments.objects.filter(
                user=request.user,
                is_completed=False
            )

            # Get submissions for these enrollments
            submissions = AssessmentSubmission.objects.filter(
                enrollment__in=enrollments,
                is_submitted=True
            ).values_list('assessment_id', flat=True)

            if value:  # If filtering for submitted assessments
                return queryset.filter(id__in=submissions)
            else:  # If filtering for non-submitted assessments
                return queryset.exclude(id__in=submissions)

        except Enrollments.DoesNotExist:
            return queryset

    class Meta:
        model = Assessment
        fields = ['course', 'title', 'type', 'due_date',
                  'created_at', 'has_submitted']


class McqQuestionFilterSet(filters.FilterSet):
    """
    Filter set for McqQuestion model.
    Allows filtering by:
    - assessment: Filter by assessment ID
    - question: Filter by question text (case-insensitive contains)
    - question_grade: Filter by question grade
    - section_number: Filter by section number
    - created_by: Filter by creator ID
    - created_at: Filter by creation date
    """
    question = filters.CharFilter(lookup_expr='icontains')
    question_grade = filters.NumberFilter()
    question_grade_min = filters.NumberFilter(
        field_name='question_grade', lookup_expr='gte')
    question_grade_max = filters.NumberFilter(
        field_name='question_grade', lookup_expr='lte')
    created_at = filters.DateTimeFilter()
    created_at_after = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = McqQuestion
        fields = ['assessment', 'question', 'question_grade',
                  'section_number', 'created_by', 'created_at']


class HandwrittenQuestionFilterSet(filters.FilterSet):
    """
    Filter set for HandwrittenQuestion model.
    Allows filtering by:
    - assessment: Filter by assessment ID
    - question_text: Filter by question text (case-insensitive contains)
    - max_grade: Filter by maximum grade
    - section_number: Filter by section number
    - created_by: Filter by creator ID
    - created_at: Filter by creation date
    """
    question_text = filters.CharFilter(lookup_expr='icontains')
    max_grade = filters.NumberFilter()
    max_grade_min = filters.NumberFilter(
        field_name='max_grade', lookup_expr='gte')
    max_grade_max = filters.NumberFilter(
        field_name='max_grade', lookup_expr='lte')
    created_at = filters.DateTimeFilter()
    created_at_after = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = HandwrittenQuestion
        fields = ['assessment', 'question_text', 'max_grade',
                  'section_number', 'created_by', 'created_at']


class DynamicMCQFilterSet(filters.FilterSet):
    """
    Filter set for DynamicMCQ model.
    Allows filtering by:
    - assessment: Filter by assessment ID
    - title: Filter by title (case-insensitive contains)
    - created_at: Filter by creation date
    """
    title = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateTimeFilter()
    created_at_after = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = DynamicMCQ
        fields = ['assessment', 'title', 'created_at']


class DynamicMCQQuestionsFilterSet(filters.FilterSet):
    """
    Filter set for DynamicMCQQuestions model.
    Allows filtering by:
    - dynamic_mcq: Filter by dynamic MCQ ID
    - question_text: Filter by question text (case-insensitive contains)
    - difficulty: Filter by difficulty level
    - question_grade: Filter by question grade
    - created_by: Filter by creator ID
    - created_at: Filter by creation date
    """
    question_text = filters.CharFilter(lookup_expr='icontains')
    question_grade = filters.NumberFilter()
    question_grade_min = filters.NumberFilter(
        field_name='question_grade', lookup_expr='gte')
    question_grade_max = filters.NumberFilter(
        field_name='question_grade', lookup_expr='lte')
    created_at = filters.DateTimeFilter()
    created_at_after = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = DynamicMCQQuestions
        fields = ['dynamic_mcq', 'question_text', 'difficulty',
                  'question_grade', 'created_by', 'created_at']
