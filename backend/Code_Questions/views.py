from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import CodingQuestion, CodingQuestionScore, TestCase
from .serializers import CodingQuestionSerializer, CodingQuestionScoreSerializer, GenerateCodingQuestionsSerializer, GenerateCodingQuestionsContextSerializer
from .utils.judge0 import run_code
from enrollments.models import Enrollments
from assessment.models import Assessment
from main.AI import generate_coding_questions_from_pdf, generate_coding_questions_from_text
from users.permissions import isTeacher
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid


class CodingQuestionListView(generics.ListCreateAPIView):
    queryset = CodingQuestion.objects.all()
    serializer_class = CodingQuestionSerializer
    permission_classes = [isTeacher]

    def create(self, request, *args, **kwargs):
        # Check if user is a teacher
        if not request.user.role == "Teacher":
            return Response(
                {"error": "Only teachers can create coding questions"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

class CodingQuestionDetailView(generics.RetrieveAPIView):
    queryset = CodingQuestion.objects.all()
    serializer_class = CodingQuestionSerializer

# class CodeSubmissionView(APIView):
#     def post(self, request, question_id):
#         try:
#             question = CodingQuestion.objects.get(id=question_id)
#         except CodingQuestion.DoesNotExist:
#             return Response({"error": "Question not found"}, status=404)

#         code = request.data.get('code')
#         enrollment_id = request.data.get('enrollment_id')

#         if not code:
#             return Response({"error": "Code is required"}, status=400)

#         if not enrollment_id:
#             return Response({"error": "Enrollment ID is required"}, status=400)

#         try:
#             enrollment = Enrollments.objects.get(id=enrollment_id)
#         except Enrollments.DoesNotExist:
#             return Response({"error": "Enrollment not found"}, status=404)

#         results = []
#         total_cases = question.test_cases.count()
#         passed_cases = 0

#         for case in question.test_cases.all():
#             result = run_code(
#                 source_code=code,
#                 stdin=case.input_data,
#                 language_id=question.language_id
#             )

#             output = (result.get("stdout") or "").strip()
#             expected = case.expected_output.strip()

#             passed = output == expected
#             if passed:
#                 passed_cases += 1

#             results.append({
#                 "input": case.input_data,
#                 "expected_output": expected,
#                 "actual_output": output,
#                 "passed": passed,
#                 "error": result.get("stderr")
#             })

#         # Calculate proportional score
#         if total_cases > 0:
#             score = int((passed_cases / total_cases) * question.score)
#         else:
#             score = 0

#         # Save or update the score in CodingQuestionScore
#         CodingQuestionScore.objects.update_or_create(
#             question=question,
#             enrollment=enrollment,
#             defaults={"score": score}
#         )

#         return Response({
#             "results": results,
#             "score": score,
#             "total_possible_score": question.score,
#             "passed_test_cases": passed_cases,
#             "total_test_cases": total_cases
#         })


class GenerateCodingQuestionsView(APIView):
    serializer_class = GenerateCodingQuestionsSerializer

    def post(self, request):
        """
        Generate coding questions from a PDF file
        Required fields in request:
        - pdf_file: The PDF file to generate questions from
        - assessment_id: UUID of the assessment to associate questions with
        - num_questions: (optional) Number of questions to generate (default: 5)
        - difficulty: (optional) Difficulty level 1-5 (default: 3)
        - language_id: (optional) Programming language ID (default: 71 for Python)
        """
        try:
            # Get required fields
            pdf_file = request.FILES.get('pdf_file')
            assessment_id = request.data.get('assessment_id')

            if not pdf_file:
                return Response(
                    {"error": "PDF file is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not assessment_id:
                return Response(
                    {"error": "Assessment ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get optional fields with defaults
            num_questions = int(request.data.get('num_questions', 5))
            difficulty = request.data.get('difficulty', '3')
            language_id = int(request.data.get('language_id', 71))

            # Validate assessment exists
            try:
                assessment = Assessment.objects.get(id=assessment_id)
            except Assessment.DoesNotExist:
                return Response(
                    {"error": "Assessment not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Generate questions from PDF
            generated_questions = generate_coding_questions_from_pdf(
                pdf_file=pdf_file,
                num_questions=num_questions,
                difficulty=difficulty,
                language_id=language_id
            )

            # Create questions and test cases in database
            created_questions = []
            for q_data in generated_questions:
                # Create the coding question
                question = CodingQuestion.objects.create(
                    id=uuid.uuid4(),
                    assessment_Id=assessment,
                    title=q_data['title'],
                    description=q_data['description'],
                    function_signature=q_data['function_signature'],
                    language_id=language_id,
                    difficulty=difficulty
                )

                # Create test cases
                for tc_data in q_data['test_cases']:
                    TestCase.objects.create(
                        id=uuid.uuid4(),
                        question=question,
                        input_data=tc_data['input_data'],
                        expected_output=tc_data['expected_output'],
                        is_public=tc_data['is_public']
                    )

                created_questions.append(question)

            # Serialize the created questions
            serializer = CodingQuestionSerializer(created_questions, many=True)

            return Response({
                "message": f"Successfully generated {len(created_questions)} coding questions",
                "questions": serializer.data
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class GenerateCodingContextQuestionsView(APIView):
    serializer_class = GenerateCodingQuestionsContextSerializer

    def post(self, request):
        """
        Generate coding questions from a PDF file
        Required fields in request:
        - Context : The Context to generate questions from
        - assessment_id: UUID of the assessment to associate questions with
        - num_questions: (optional) Number of questions to generate (default: 5)
        - difficulty: (optional) Difficulty level 1-5 (default: 3)
        - language_id: (optional) Programming language ID (default: 71 for Python)
        """
        try:
            # Get required fields
            context = request.data.get('context')
            assessment_id = request.data.get('assessment_id')

            if not context:
                return Response(
                    {"error": "Context is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not assessment_id:
                return Response(
                    {"error": "Assessment ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get optional fields with defaults
            num_questions = int(request.data.get('num_questions', 5))
            difficulty = request.data.get('difficulty', '3')
            language_id = int(request.data.get('language_id', 71))

            # Validate assessment exists
            try:
                assessment = Assessment.objects.get(id=assessment_id)
            except Assessment.DoesNotExist:
                return Response(
                    {"error": "Assessment not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Generate questions from PDF
            generated_questions = generate_coding_questions_from_text(
                text=context,
                num_questions=num_questions,
                difficulty=difficulty,
                language_id=language_id
            )

            # Create questions and test cases in database
            created_questions = []
            for q_data in generated_questions:
                # Create the coding question
                question = CodingQuestion.objects.create(
                    id=uuid.uuid4(),
                    assessment_Id=assessment,
                    title=q_data['title'],
                    description=q_data['description'],
                    function_signature=q_data['function_signature'],
                    language_id=language_id,
                    difficulty=difficulty
                )

                # Create test cases
                for tc_data in q_data['test_cases']:
                    TestCase.objects.create(
                        id=uuid.uuid4(),
                        question=question,
                        input_data=tc_data['input_data'],
                        expected_output=tc_data['expected_output'],
                        is_public=tc_data['is_public']
                    )

                created_questions.append(question)

            # Serialize the created questions
            serializer = CodingQuestionSerializer(created_questions, many=True)

            return Response({
                "message": f"Successfully generated {len(created_questions)} coding questions",
                "questions": serializer.data
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# class CodequestionScoreListView(generics.ListAPIView):
    # queryset = CodingQuestionScore.objects.all()
    # serializer_class = CodingQuestionScoreSerializer