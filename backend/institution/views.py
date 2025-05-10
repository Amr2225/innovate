# Django
from django.contrib.auth import get_user_model
from django.core.cache import cache

# DRF
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

# Institution Serializers
from institution.serializers import InstitutionRegisterSeralizer, InstitutionUserSeralizer

# Permissions
from users.permissions import isInstitution

# Python
import io
import csv
import secrets


User = get_user_model()


class InstitutionRegisterView(generics.CreateAPIView):
    model = User
    serializer_class = InstitutionRegisterSeralizer


class BulkUserImportView(generics.CreateAPIView):
    permission_classes = [isInstitution]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = InstitutionUserSeralizer

    def create(self, request):
        csv_file = request.FILES.get('file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'Please upload a valid CSV file'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Track results
        created_users = []
        errors = []

        # Process CSV file
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = list(csv.DictReader(io_string, delimiter=","))

            # Process each row from the dictionary
            for row in reader:
                # Clean the data - strip whitespace and handle empty strings
                cleaned_row = {k: v.strip() if v else None for k,
                               v in row.items()}

                # Validate row data
                serializer = self.get_serializer(
                    data=cleaned_row, context={'request': request})

                if serializer.is_valid():
                    # Create user with institution relationship
                    self.perform_create(serializer)
                    created_users.append(serializer.data)
                else:
                    if 'national_id' in serializer.errors:
                        try:
                            existing_user = User.objects.exclude(
                                institution__in=[request.user]).get(national_id=serializer.data['national_id'])
                            existing_user.institution.add(request.user)
                            created_users.append(
                                self.get_serializer(existing_user).data)
                        except User.DoesNotExist:
                            print("user doesn't exist")
                            errors.append({
                                'row': serializer.data,
                                'errors': serializer.errors
                            })
                    else:
                        errors.append({
                            'row': serializer.data,
                            'errors': serializer.errors
                        })

            # Return results
            return Response({
                'success': True,
                'created_count': len(created_users),
                'created_users': created_users,
                'error_count': len(errors),
                'errors': errors
            }, status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'page': self.page.number,
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'total_items': self.page.paginator.count,
            'next': self.page.next_page_number() if self.page.has_next() else None,
            'previous': self.page.previous_page_number() if self.page.has_previous() else None
        })


class InstitutionUserView(generics.ListCreateAPIView):
    # model = User
    # queryset = User.objects.all()
    serializer_class = InstitutionUserSeralizer
    permission_classes = [isInstitution]
    pagination_class = Pagination

    def get_queryset(self):
        print(secrets.token_urlsafe(48))
        user = self.request.user
        return User.objects.filter(institution=user)
