from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import CodingQuestion, TestCase, CodingQuestionScore
from .serializers import (
    CodingQuestionSerializer,
    TestCaseSerializer,
    CodingQuestionScoreSerializer,
    GenerateCodingQuestionsSerializer
)
from main.AI import generate_coding_questions, evaluate_coding_answer
from assessment.models import Assessment
from enrollments.models import Enrollments
import logging

logger = logging.getLogger(__name__)

# Create your views here.

# Views will be added here

class GenerateCodingQuestionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = GenerateCodingQuestionsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get validated data
            lecture_ids = serializer.validated_data.get('lecture_ids')
            context = serializer.validated_data.get('context')
            assessment_id = serializer.validated_data['assessment_id']
            grade = serializer.validated_data['grade']
            section_number = serializer.validated_data['section_number']
            num_questions = serializer.validated_data.get('num_questions', 3)

            # Get the assessment
            assessment = get_object_or_404(Assessment, id=assessment_id)

            # Generate questions using AI
            questions = generate_coding_questions(
                lecture_ids=lecture_ids,
                context=context,
                num_questions=num_questions,
                grade=grade,
                section_number=section_number
            )

            # Create coding questions in the database
            created_questions = []
            for question_data in questions:
                # Create the coding question
                question = CodingQuestion.objects.create(
                    title=question_data['title'],
                    description=question_data['description'],
                    function_signature=question_data['function_signature'],
                    language_id=question_data['language_id'],
                    max_grade=question_data['max_grade'],
                    assessment=assessment,
                    created_by=request.user
                )

                # Create test cases
                for test_case_data in question_data['test_cases']:
                    TestCase.objects.create(
                        question=question,
                        input_data=test_case_data['input'],
                        expected_output=test_case_data['output'],
                        is_public=test_case_data['is_public']
                    )

                created_questions.append(question)

            # Serialize and return the created questions
            serializer = CodingQuestionSerializer(created_questions, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error generating coding questions: {str(e)}")
            return Response(
                {"error": "Failed to generate coding questions"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SubmitCodingAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, question_id):
        try:
            # Get the question and enrollment
            question = get_object_or_404(CodingQuestion, id=question_id)
            enrollment = get_object_or_404(
                Enrollments,
                user=request.user,
                course=question.assessment.course
            )

            # Get submitted code
            submitted_code = request.data.get('code')
            if not submitted_code:
                return Response(
                    {"error": "No code submitted"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get test cases
            test_cases = [
                {
                    "input": tc.input_data,
                    "output": tc.expected_output,
                    "is_public": tc.is_public
                }
                for tc in question.test_cases.all()
            ]

            # Evaluate the code
            evaluation_result = evaluate_coding_answer(
                function_signature=question.function_signature,
                submitted_code=submitted_code,
                language_id=question.language_id,
                test_cases=test_cases
            )

            # Create or update the score
            score, created = CodingQuestionScore.objects.update_or_create(
                question=question,
                enrollment=enrollment,
                defaults={
                    'score': evaluation_result['score'],
                    'feedback': evaluation_result['feedback'],
                    'submitted_code': submitted_code,
                    'test_results': evaluation_result['test_results']
                }
            )

            # Return the evaluation result
            serializer = CodingQuestionScoreSerializer(score)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error evaluating code: {str(e)}")
            return Response(
                {"error": "Failed to evaluate code"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CodingQuestionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CodingQuestionSerializer

    def get_queryset(self):
        assessment_id = self.request.query_params.get('assessment_id')
        if not assessment_id:
            return CodingQuestion.objects.none()
        return CodingQuestion.objects.filter(assessment_id=assessment_id)

class CodingQuestionDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CodingQuestionSerializer
    queryset = CodingQuestion.objects.all()
