from django_filters import rest_framework as filters
from courses.models import Course


class CourseFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    semester = filters.NumberFilter()
    semester_after = filters.NumberFilter(
        field_name='semester', lookup_expr='gte')
    semester_before = filters.NumberFilter(
        field_name='semester', lookup_expr='lte')
    created_at = filters.DateTimeFilter()
    created_at_after = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Course
        fields = ['name', 'instructors', 'created_at', 'semester']
