# Django
import uuid
from django.contrib.auth import get_user_model
from django.conf import settings

# DRF
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import requests

# Institution Serializers
from institution.serializers import InstitutionRegisterSeralizer, InstitutionUserSeralizer

# Permissions
from users.permissions import isInstitution

# Python
import io
import csv


User = get_user_model()


class InstitutionRegisterView(generics.CreateAPIView):
    model = User
    serializer_class = InstitutionRegisterSeralizer


class WebhookView(views.APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        print("Type: ", request.data['type'])
        print("Transaction ID: ", request.data['obj']['id'])
        print("Success: ", request.data['obj']['success'])
        print("Transaction type: ",
              request.data['obj']['source_data']['sub_type'])
        print("Number: ",
              request.data['obj']['source_data']['pan'])
        print("Created At: ", request.data['obj']['created_at'])

        return Response(status=status.HTTP_200_OK)


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
                    # instance = serializer.save()
                    # created_users.append(
                    #     InstitutionUserSeralizer(instance).data)
                else:
                    if 'national_id' in serializer.errors:
                        try:
                            existing_user = User.objects.exclude(
                                institution__in=[request.user]).get(national_id=serializer.data['national_id'])
                            # existing_user = User.objects.get(
                            #     national_id=serializer.data['national_id'])
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
                        # existing_user = User.objects.filter(national_id=cleaned_row['national_id'])
                        # Track errors for this row
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


class InstitutionUserView(generics.ListCreateAPIView):
    # model = User
    # queryset = User.objects.all()
    serializer_class = InstitutionUserSeralizer
    permission_classes = [isInstitution]

    def get_queryset(self):
        print(secrets.token_urlsafe(48))
        user = self.request.user
        return User.objects.filter(institution=user)


# class InititationPaymentView(generics.CreateAPIView):
#     permission_classes = [isInstitution]
#     serializer_class = InititationPaymentSerializer

#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

class TestRequestView(views.APIView):
    def post(self, request, *args, **kwargs):
        print("payment request")
        try:
            payload = {
                'amount': 300000,
                'currency': 'EGP',
                "payment_methods": [
                    4877887,
                    4877830
                ],
                "items": [
                    {
                        "name": "Credits",
                        "amount": 200,
                        "description": "Innovate Credits",
                        "quantity": 1500,
                        "plan_id": "1234567890"
                    }
                ],
                "billing_data": {
                    "first_name": "cairo",
                    "last_name": "cairo",
                    "email": "cairo@gmail.com",
                    "phone_number": "+2010101010"
                },
                "special_reference": str(uuid.uuid4()),
                "redirection_url": f"{settings.CLIENT_URL}/institution-register/",
                "expiration": 3600
            }

            response = requests.post(
                'https://accept.paymob.com/v1/intention/',
                json=payload,
                headers={'Authorization': f'Token {settings.PAYMOB_SK}'}
            )
            print(response.json())

            client_secret = response.json().get('client_secret')

            URL = f"https://accept.paymob.com/unifiedcheckout/?publicKey={settings.PAYMOB_PK}&clientSecret={client_secret}"

            # Return the response from the external service
            return Response(URL, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
