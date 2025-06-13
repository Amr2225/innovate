from users.models import User
from django_filters import rest_framework as filters


class InstituionUserFilter(filters.FilterSet):
    first_name = filters.CharFilter(lookup_expr='icontains')
    middle_name = filters.CharFilter(lookup_expr='icontains')
    last_name = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    role = filters.CharFilter(lookup_expr='icontains')
    institution = filters.CharFilter(lookup_expr='icontains')
    national_id = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'email',
                  'role', 'institution', 'national_id']
