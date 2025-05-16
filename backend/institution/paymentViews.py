# Django
from django.conf import settings
from django.core.cache import cache

# DRF
from rest_framework import views, status, generics
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

# Python
import uuid
import requests

from institution.models import Plan
from institution.paymentPayload import get_payment_payload
from institution.serializers import InstitutionGeneratePaymentSerializer, InstitutionBuyCreditsSerializer

from users.permissions import isInstitution

from institution.models import Payment


class InstitutionBuyCreditsView(generics.CreateAPIView):
    permission_classes = [isInstitution]
    model = Payment
    serializer_class = InstitutionBuyCreditsSerializer


class InstitutionPaymentWebhookView(views.APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        hmac = request.query_params.get('hmac')
        print("HMAC: ", hmac)
        print("Type: ", request.data['type'])
        print("Transaction ID: ", request.data['obj']['id'])
        print("Success: ", request.data['obj']['success'])
        print("Transaction type: ",
              request.data['obj']['source_data']['sub_type'])
        print("Number: ",
              request.data['obj']['source_data']['pan'])
        print("Created At: ", request.data['obj']['created_at'])

        data = {
            "transaction_id": request.data['obj']['id'],
            "success": request.data['obj']['success'],
            "transaction_type": request.data['obj']['source_data']['sub_type'],
            "number": request.data['obj']['source_data']['pan'],
            # TODO: May be delete created_at
            "created_at": request.data['obj']['created_at'],
            "plan_id": request.data['obj']['payment_key_claims']['extra']['plan_id'],
            "order_id": request.data['obj']['payment_key_claims']['order_id'],
            "credits_amount": request.data['obj']['order']['items'][0]['quantity']
        }

        cache.set(hmac, data, timeout=60 * 15)

        return Response(status=status.HTTP_200_OK)


class InstitutionVerifyPaymentView(views.APIView):
    def post(self, request, *args, **kwargs):
        try:
            hmac = request.data.get('hmac')
            data = cache.get(hmac)
            print("Saved Data: ", data)
            if not data:
                return Response(
                    {'error': 'Invalid HMAC'}, status=status.HTTP_400_BAD_REQUEST)
            if not data['success']:
                return Response(
                    {'error': 'Payment Failed'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InstitutionGeneratePaymentIntentView(views.APIView):
    serializer_class = InstitutionGeneratePaymentSerializer

    # Validate the plan ID
    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')

        # If the redirection URL is not provided, use the default one redirects the registration page
        redirection_url = request.data.get(
            'redirection_url', f"{settings.CLIENT_URL}/institution-register/{plan_id}")

        # If the plan ID is not provided, return an error
        if not plan_id:
            return Response(
                {'errors': "Plan ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            plan = Plan.objects.get(id=plan_id)
            if (plan.minimum_credits > request.data.get('credits')):
                return Response(
                    {'errors': f"Minimum credits for {plan.type} plan is {plan.minimum_credits}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Plan.DoesNotExist:
            return Response(
                {'errors': "Invalid plan ID"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate The Request Data
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            payload = get_payment_payload(
                plan_id, serializer.validated_data, redirection_url)

            response = requests.post(
                'https://accept.paymob.com/v1/intention/',
                json=payload,
                headers={'Authorization': f'Token {settings.PAYMOB_SK}'}
            )
            # print(response.json())

            client_secret = response.json().get('client_secret')

            URL = f"https://accept.paymob.com/unifiedcheckout/?publicKey={settings.PAYMOB_PK}&clientSecret={client_secret}"

            # Return the response from the external service
            return Response({'url': URL}, status=status.HTTP_200_OK)

        except ValidationError as e:
            print(e)
            return Response(
                {'errors': "Invalid Data Please try again"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except requests.RequestException:
            return Response(
                {'error': 'Something went wrong, please try again later'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
