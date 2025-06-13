import time
import base64
import json
from rest_framework.parsers import MultiPartParser, FormParser
from drf_sse import SSEMixin, SSEResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from HandwrittenQuestion.models import HandwrittenQuestion
from assessment.models import Assessment
from enrollments.models import Enrollments
from users.permissions import isStudent
from django.core.cache import cache
from assessment.authentication import EventStreamAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


class MyView(SSEMixin, APIView):
    """
    Server-Sent Events endpoint for receiving updates.
    """
    authentication_classes = [EventStreamAuthentication]

    @extend_schema(
        description="SSE endpoint for streaming data",
        parameters=[
            OpenApiParameter(
                name='token',
                description='JWT token for authentication',
                required=True,
                type=str,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='assessment_id',
                description='ID of the assessment',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='question_id',
                description='ID of the question',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            ),
        ],
        responses={200: None},
    )
    def get(self, request, assessment_id, question_id, token):
        # Authenticate user with the token
        user = self.authentication_classes[0]().authenticate(token)
        if not user:
            return Response({'error': 'Authentication failed'}, status=401)

        request.user = user

        print("USERID", user.id)
        print(assessment_id)
        print(question_id)
        print(token)
        request.is_disconnected = lambda: False

        def iter_data():
            cache_key = f"temp_images_{user.id}_{assessment_id}_{question_id}"
            cached_images = cache.get(cache_key, [])
            if cached_images:
                for image in cached_images:
                    image.seek(0)
                    image_content = base64.b64encode(
                        image.read()).decode('utf-8')
                    # yield f"data:image/jpeg;base64,{image_content}\n\n"
                    yield json.dumps({'image': image_content})
                    time.sleep(1)
                cache.delete(cache_key)
            # else:
            #     iter_data = 'This is a server-sent events response'.split()
            #     for part in iter_data:
            #         yield part
            #         time.sleep(1)

        return SSEResponse(iter_data())


class TempUploadImage(APIView):
    """
    API endpoint for uploading temporary images for handwritten questions.
    """
    permission_classes = [isStudent]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        description="Upload a temporary image for a handwritten question",
        parameters=[
            OpenApiParameter(
                name='assessment_id',
                description='ID of the assessment',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='question_id',
                description='ID of the question',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            ),
        ],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary'
                    }
                },
                'required': ['image']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'total_images': {'type': 'integer'},
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                }
            }
        }
    )
    def post(self, request, assessment_id, question_id):
        # Get user from token
        user = request.user

        # Validate assessment exists and user has access
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            enrollment = Enrollments.objects.get(
                user=user, course=assessment.course)
        except (Assessment.DoesNotExist, Enrollments.DoesNotExist):
            return Response({"error": "Invalid assessment or no access"}, status=400)

        # Validate assessment is accepting submissions
        if not assessment.accepting_submissions:
            return Response({"error": "Assessment is not accepting submissions"}, status=400)

        # Validate question exists and is handwritten type
        try:
            question = HandwrittenQuestion.objects.get(
                id=question_id, assessment=assessment)
        except HandwrittenQuestion.DoesNotExist:
            return Response({"error": "Invalid question or not handwritten type"}, status=400)

        # Get image from request
        image = request.FILES.get('image')
        if not image:
            return Response({"error": "No image provided"}, status=400)

        # Create cache key
        cache_key = f"temp_images_{user.id}_{assessment_id}_{question_id}"

        # Get existing images from cache or initialize empty list
        cached_images = cache.get(cache_key, [])

        # Add new image to list
        cached_images.append(image)

        # Store updated list in cache
        cache.set(cache_key, cached_images)

        return Response({
            "message": "Image uploaded successfully",
            "total_images": len(cached_images)
        })
