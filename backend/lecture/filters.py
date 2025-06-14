from django_filters import rest_framework as filters
from .models import Lecture
from assessment.models import Assessment


class LectureFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    chapter = filters.NumberFilter()
    chapter_after = filters.NumberFilter(
        field_name='chapter', lookup_expr='gte')
    created_at = filters.DateTimeFilter()
    created_at_after = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte')
    assessment_id = filters.UUIDFilter(method='filter_by_assessment')

    def filter_by_assessment(self, queryset, name, value):
        try:
            assessment = Assessment.objects.get(id=value)
            return queryset.filter(chapter__course=assessment.course)
        except Assessment.DoesNotExist:
            return queryset.none()

    class Meta:
        model = Lecture
        fields = ['id', 'title', 'description',
                  'chapter', 'created_at', 'assessment_id']
