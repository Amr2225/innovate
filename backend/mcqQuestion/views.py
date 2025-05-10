from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from .models import McqQuestion
from .serializers import McqQuestionSerializer


class McqQuestionPermission(permissions.BasePermission):
    """Custom permission class for MCQ questions"""
    
    def has_permission(self, request, view):
        # Anyone authenticated can view
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Only teachers and institutions can create
        return request.user.role in ["Teacher", "Institution"]
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        # Anyone authenticated can view
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only the creator or the assessment institution can modify/delete
        return obj.created_by == user or obj.assessment.institution == user


class McqQuestionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = McqQuestionSerializer
    permission_classes = [McqQuestionPermission]
    filterset_fields = ['created_by', 'assessment']

    def get_queryset(self):
        user = self.request.user
        assessment_id = self.kwargs.get('assessment_id')
        base_queryset = McqQuestion.objects.filter(
            assessment_id=assessment_id
        ).select_related('assessment', 'created_by')

        if user.role in ["Teacher", "Institution"]:
            return base_queryset
        elif user.role == "Student":
            # Students can only see questions from assessments that are past due
            return base_queryset.filter(
                assessment__due_date__lte=timezone.now(),
                assessment__course__enrolled_students=user
            )
        return McqQuestion.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        assessment = serializer.validated_data.get('assessment')
        
        # Check if assessment exists and is not past due
        if assessment.due_date < timezone.now():
            raise ValidationError("Cannot create questions for past-due assessments")
            
        # Check if user has permission to create questions for this assessment
        if user != assessment.institution and not user.role in ["Teacher", "Institution"]:
            raise PermissionDenied(
                "You don't have permission to create questions for this assessment"
            )
            
        serializer.save(created_by=user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        
        # Remove answer keys from response if user is a student
        if request.user.role == "Student":
            for item in data:
                item.pop('answer_key', None)
        
        return Response({
            "count": len(data),
            "results": data
        })


class McqQuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific MCQ question.
    Only the creator or assessment institution can modify it.
    """
    serializer_class = McqQuestionSerializer
    permission_classes = [McqQuestionPermission]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        base_queryset = McqQuestion.objects.select_related('assessment', 'created_by')

        if user.role in ["Teacher", "Institution"]:
            return base_queryset.filter(
                Q(created_by=user) | Q(assessment__institution=user)
            )
        elif user.role == "Student":
            return base_queryset.filter(
                assessment__due_date__lte=timezone.now(),
                assessment__course__enrolled_students=user
            )
        return McqQuestion.objects.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Remove answer key from response if user is a student
        if request.user.role == "Student":
            data.pop('answer_key', None)
            
        return Response(data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if assessment is past due
        if instance.assessment.due_date < timezone.now():
            raise ValidationError("Cannot modify questions for past-due assessments")
            
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Re-fetch instance to get updated data
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if assessment is past due
        if instance.assessment.due_date < timezone.now():
            raise ValidationError("Cannot delete questions from past-due assessments")
            
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class GenerateMCQsView(generics.GenericAPIView):
    """
    View for generating MCQ questions using AI.
    """
    def validate_num_questions(self, num_questions):
        """Validate number of questions"""
        try:
            num = int(num_questions)
            if num < 1:
                raise ValidationError("Number of questions must be positive")
            if num > 50:  # Add reasonable limit
                raise ValidationError("Maximum 50 questions allowed per request")
            return num
        except (TypeError, ValueError):
            raise ValidationError("Number of questions must be a valid integer")

    def post(self, request, *args, **kwargs):
        """
        Generate MCQ questions using AI based on provided context.
        POST /mcq-questions/generate-mcqs/
        
        Request body:
        {
            "context": "Educational content to generate questions from",
            "num_questions": 10 (optional, default=10, max=50)
        }
        """
        from .AI import client, dmcq, extract_json
        
        # Get and validate context
        context = request.data.get('context', '').strip()
        if not context:
            raise ValidationError({"context": "Context is required to generate MCQs"})
        
        # Get and validate number of questions
        num_questions = self.validate_num_questions(
            request.data.get('num_questions', 10)
        )

        # Update the user message with the provided context and number of questions
        try:
            dmcq[1]['content'] = f"""
            context: {context}

            Based on the provided context, generate {num_questions} multiple-choice questions. Your response must be strictly in the following JSON format:

            [{{"question": "<question text>",
              "options": ["<option 1>", "<option 2>", "<option 3>", "<option 4>"],
              "correct_answer": "<correct option number>"}}]
            """

            # Make API call to generate MCQs
            completion = client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=dmcq,
                temperature=0.7,  # Lower temperature for more consistent output
                max_tokens=1000,  # Increased for longer responses
            )

            # Extract and parse JSON from response
            mcq_data = extract_json(completion.choices[0].message.content)
            
            # Validate MCQ data structure
            if not isinstance(mcq_data, list):
                raise ValidationError("Invalid response format from AI")
                
            for q in mcq_data:
                if not isinstance(q, dict):
                    raise ValidationError("Invalid question format in AI response")
                if 'question' not in q or 'options' not in q or 'correct_answer' not in q:
                    raise ValidationError("Missing required fields in AI response")
                if not isinstance(q['options'], list) or len(q['options']) != 4:
                    raise ValidationError("Invalid options format in AI response")
            
            return Response({
                'mcqs': mcq_data[:num_questions],  # Ensure we don't exceed requested number
                'num_questions': len(mcq_data[:num_questions]),
                'context': context
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({
                'error': str(e),
                'error_type': 'validation_error'
            }, status=status.HTTP_400_BAD_REQUEST)
        except ConnectionError:
            return Response({
                'error': 'Failed to connect to AI service',
                'error_type': 'connection_error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'error': 'Internal server error occurred',
                'error_type': 'internal_error',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


