from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Assessment, AssessmentScore
from .serializers import AssessmentSerializer, AssessmentScoreSerializer, AssessmentListSerializer
from .filters import AssessmentFilterSet
from enrollments.models import Enrollments
from mcqQuestion.models import McqQuestion
from mcqQuestion.serializers import McqQuestionSerializer
from MCQQuestionScore.models import MCQQuestionScore
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.http import Http404
from HandwrittenQuestion.models import HandwrittenQuestionScore
from django.utils import timezone
from AssessmentSubmission.models import AssessmentSubmission
from django.apps import apps

# ----------------------
# Assessment Views
# ----------------------


class AssessmentPermission(permissions.BasePermission):
    """Custom permission class for assessments"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Allow all authenticated users to view
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only teachers and institutions can create/edit
        return request.user.role in ["Teacher", "Institution"]

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Students can only view their own assessments
        if request.user.role == "Student":
            return Enrollments.objects.filter(
                user=request.user,
                course=obj.course
            ).exists()

        # Teachers can access assessments for their courses
        if request.user.role == "Teacher":
            return obj.course.teacher == request.user.teacher

        # Institutions can access assessments for their courses
        if request.user.role == "Institution":
            return obj.course.institution == request.user.institution

        return False


class AssessmentListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint to list and create assessments.

    GET /api/assessments/
    List all assessments with filtering options:
    - course: Filter by course ID
    - title: Filter by assessment title (case-insensitive contains)
    - type: Filter by assessment type
    - due_date: Filter by due date
    - accepting_submissions: Filter by whether assessment is accepting submissions
    - created_at: Filter by creation date

    POST /api/assessments/
    Create a new assessment.

    Parameters:
    - course: Course ID
    - title: Assessment title
    - description: Assessment description
    - type: Assessment type
    - grade: Assessment grade
    - due_date: Due date
    - accepting_submissions: Whether assessment is accepting submissions

    Returns:
    ```json
    {
        "id": "uuid",
        "course": "uuid",
        "title": "string",
        "description": "string",
        "type": "string",
        "grade": "decimal",
        "due_date": "datetime",
        "accepting_submissions": "boolean",
        "created_at": "datetime",
        "updated_at": "datetime"
    }
    ```

    Status Codes:
    - 200: Successfully retrieved assessments
    - 201: Successfully created assessment
    - 400: Invalid input data
    - 403: Not authorized to create assessment

    Permissions:
    - Students: Can view assessments for courses they're enrolled in
    - Teachers: Can manage assessments for courses they teach
    - Institutions: Can manage assessments for their courses
    """
    serializer_class = AssessmentListSerializer
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]
    filterset_class = AssessmentFilterSet

    def get_queryset(self):
        user = self.request.user
        course_id = self.kwargs.get('course_id')

        base_queryset = Assessment.objects.all()

        # Filter by course if course_id is provided in URL
        if course_id:
            base_queryset = base_queryset.filter(course_id=course_id)

        if user.role == "Student":
            # Students can only see assessments for courses they are enrolled in
            return base_queryset.filter(
                course__enrollments__user=user
            ).distinct()

        elif user.role == "Teacher":
            # Teachers can see assessments for courses they teach
            return base_queryset.filter(
                course__instructors=user
            )

        elif user.role == "Institution":
            # Institutions can see assessments for their courses
            return base_queryset.filter(
                course__institution=user
            )

        return Assessment.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssessmentSerializer
        return AssessmentListSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied(
                "Only teachers and institutions can create assessments")

        # Check if user has permission to create assessment for this course
        course = serializer.validated_data['course']
        if user.role == "Teacher" and not course.instructors.filter(id=user.id).exists():
            raise PermissionDenied(
                "You can only create assessments for courses you teach")
        if user.role == "Institution" and course.institution == user.institution:
            raise PermissionDenied(
                "You can only create assessments for your institution's courses")

        serializer.save()


class AssessmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == "Student":
            # Students can only see assessments for courses they are enrolled in
            return Assessment.objects.filter(
                course__enrollments__user=user
            ).distinct()

        elif user.role == "Teacher":
            # Teachers can see assessments for courses they teach
            return Assessment.objects.filter(
                course__teacher=user.teacher
            )

        elif user.role == "Institution":
            # Institutions can see assessments for their courses
            return Assessment.objects.filter(
                course__institution=user.institution
            )

        return Assessment.objects.none()

    def perform_update(self, serializer):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied(
                "Only teachers and institutions can update assessments")

        # Check if user has permission to update assessment for this course
        course = serializer.instance.course
        if user.role == "Teacher" and course.teacher != user.teacher:
            raise PermissionDenied(
                "You can only update assessments for courses you teach")
        if user.role == "Institution" and course.institution != user.institution:
            raise PermissionDenied(
                "You can only update assessments for your institution's courses")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied(
                "Only teachers and institutions can delete assessments")

        # Check if user has permission to delete assessment for this course
        course = instance.course
        if user.role == "Teacher" and course.teacher != user.teacher:
            raise PermissionDenied(
                "You can only delete assessments for courses you teach")
        if user.role == "Institution" and course.institution != user.institution:
            raise PermissionDenied(
                "You can only delete assessments for your institution's courses")

        instance.delete()

# ----------------------
# Assessment Score Views
# ----------------------


class AssessmentScoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == "Student":
            # Students can only see their own scores
            return AssessmentScore.objects.filter(
                enrollment__user=user
            )

        elif user.role == "Teacher":
            # Teachers can see scores for their courses
            return AssessmentScore.objects.filter(
                assessment__course__teacher=user.teacher
            )

        elif user.role == "Institution":
            # Institutions can see scores for their courses
            return AssessmentScore.objects.filter(
                assessment__course__institution=user.institution
            )

        return AssessmentScore.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "Student":
            raise PermissionDenied(
                "Only students can submit assessment scores")

        assessment = Assessment.objects.get(
            id=self.request.data.get('assessment'))

        # Check if the assessment is still accepting submissions
        if not assessment.accepting_submissions:
            raise PermissionDenied(
                "This assessment is no longer accepting submissions as it has passed its due date")

        # Check if student is enrolled in the course
        is_completed = self.request.query_params.get(
            'is_completed', 'false').lower() == 'true'
        if not Enrollments.objects.filter(
            user=user,
            course=assessment.course,
            is_completed=is_completed
        ).exists():
            raise PermissionDenied("You are not enrolled in this course")

        enrollment = Enrollments.objects.get(
            user=user, course=assessment.course)
        # Check if student has already submitted
        if AssessmentScore.objects.filter(assessment=assessment, enrollment=enrollment).exists():
            raise PermissionDenied(
                "You have already submitted this assessment")

        serializer.save(enrollment=enrollment)


class AssessmentScoreDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == "Student":
            # Students can only see their own scores
            return AssessmentScore.objects.filter(
                enrollment__user=user
            )

        elif user.role == "Teacher":
            # Teachers can see scores for their courses
            return AssessmentScore.objects.filter(
                assessment__course__teacher=user.teacher
            )

        elif user.role == "Institution":
            # Institutions can see scores for their courses
            return AssessmentScore.objects.filter(
                assessment__course__institution=user.institution
            )

        return AssessmentScore.objects.none()

    def perform_update(self, serializer):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied(
                "Only teachers and institutions can update assessment scores")

        # Check if user has permission to update score for this course
        course = serializer.instance.assessment.course
        if user.role == "Teacher" and course.teacher != user.teacher:
            raise PermissionDenied(
                "You can only update scores for courses you teach")
        if user.role == "Institution" and course.institution != user.institution:
            raise PermissionDenied(
                "You can only update scores for your institution's courses")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied(
                "Only teachers and institutions can delete assessment scores")

        # Check if user has permission to delete score for this course
        course = instance.assessment.course
        if user.role == "Teacher" and course.teacher != user.teacher:
            raise PermissionDenied(
                "You can only delete scores for courses you teach")
        if user.role == "Institution" and course.institution != user.institution:
            raise PermissionDenied(
                "You can only delete scores for your institution's courses")

        instance.delete()


class AssessmentQuestionsAPIView(generics.ListAPIView):
    """
    API endpoint to get all questions for a specific assessment.

    This endpoint returns all questions (MCQ, Dynamic MCQ, and Handwritten) for an assessment
    based on the user's role and permissions.

    GET /api/assessments/{assessment_id}/questions/

    Parameters:
    - assessment_id (UUID): The ID of the assessment
    - is_completed (boolean, optional): Filter by enrollment completion status (for students)

    Returns:
    ```json
    {
        "questions": [
            {
                "id": "uuid",
                "type": "mcq|dynamic_mcq|handwritten",
                "question": "string",
                "options": ["string"],  // For MCQ and Dynamic MCQ
                "answer_key": "string",  // Only for teachers/institutions
                "question_grade": "string",  // For MCQ
                "max_grade": "string",  // For Handwritten
                "section_number": "integer",
                "difficulty": "string"  // For Dynamic MCQ
            }
        ]
    }
    ```

    Status Codes:
    - 200: Successfully retrieved questions
    - 403: Not authorized to view questions
    - 404: Assessment not found

    Permissions:
    - Students: Can view questions for courses they're enrolled in
    - Teachers: Can view questions for courses they teach
    - Institutions: Can view questions for their courses
    """
    serializer_class = McqQuestionSerializer
    permission_classes = [AssessmentPermission]

    def get_queryset(self):
        assessment_id = self.kwargs.get('pk')
        user = self.request.user

        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            return McqQuestion.objects.none()

        # Check permissions
        if user.role == "Student":
            # Students can only view questions for courses they're enrolled in
            is_completed = self.request.query_params.get(
                'is_completed', 'false').lower() == 'true'
            if not Enrollments.objects.filter(
                user=user,
                course=assessment.course,
                is_completed=is_completed
            ).exists():
                return McqQuestion.objects.none()
        elif user.role == "Teacher":
            # Teachers can view questions for courses they teach
            if not assessment.course.instructors.filter(id=user.id).exists():
                return McqQuestion.objects.none()
        elif user.role == "Institution":
            # Institution can view questions for their courses
            if assessment.course.institution != user:
                return McqQuestion.objects.none()
        else:
            return McqQuestion.objects.none()

        # Get all questions for the assessment
        return McqQuestion.objects.filter(assessment=assessment)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Add request to context for role-based answer key visibility
        context['request'] = self.request
        return context


class StudentGradesAPIView(generics.GenericAPIView):
    """
    API endpoint to get a student's grades for a specific assessment.

    This endpoint returns detailed information about a student's performance in an assessment,
    including their answers, scores, and feedback for each question.

    GET /api/assessments/{assessment_id}/student-grades/

    Parameters:
    - assessment_id (UUID): The ID of the assessment

    Returns:
    ```json
    {
        "assessment_id": "uuid",
        "assessment_title": "string",
        "questions": [
            {
                "question_id": "uuid",
                "question_text": "string",
                "type": "mcq|handwritten",
                "student_answer": "string",
                "is_correct": "boolean",  // For MCQ
                "score": "string",
                "max_score": "string",
                "options": ["string"],  // For MCQ
                "correct_answer": "string",  // For teachers/institutions
                "extracted_text": "string",  // For Handwritten
                "feedback": "string",  // For Handwritten
                "answer_image": "url"  // For Handwritten
            }
        ],
        "total_score": "float",
        "total_max_score": "float"
    }
    ```

    Status Codes:
    - 200: Successfully retrieved grades
    - 400: Assessment not submitted
    - 403: Not authorized to view grades
    - 404: Assessment or score not found

    Permissions:
    - Students: Can view their own grades
    - Teachers: Can view grades for their courses
    - Institutions: Can view grades for their courses
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            assessment_id = kwargs.get('pk')

            if not assessment_id:
                return Response({
                    'detail': 'assessment_id is required in URL'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the assessment
            try:
                assessment = Assessment.objects.get(id=assessment_id)
            except Assessment.DoesNotExist:
                return Response({
                    'detail': 'Assessment not found'
                }, status=status.HTTP_404_NOT_FOUND)

            # Get student's enrollment
            try:
                is_completed = request.query_params.get(
                    'is_completed', 'false').lower() == 'true'
                enrollment = Enrollments.objects.get(
                    user=request.user,
                    course=assessment.course,
                    is_completed=is_completed
                )
            except Enrollments.DoesNotExist:
                return Response({
                    'detail': 'You are not enrolled in this course'
                }, status=status.HTTP_403_FORBIDDEN)

            # Check if assessment has been submitted
            try:
                submission = AssessmentSubmission.objects.get(
                    assessment=assessment,
                    enrollment=enrollment
                )
                if not submission.is_submitted:
                    return Response({
                        'detail': 'You haven\'t submitted this assessment yet'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except AssessmentSubmission.DoesNotExist:
                return Response({
                    'detail': 'You haven\'t submitted this assessment yet'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the assessment score
            try:
                assessment_score = AssessmentScore.objects.select_related(
                    'assessment__course',
                    'enrollment__user'
                ).get(
                    enrollment=enrollment,
                    assessment=assessment
                )
            except AssessmentScore.DoesNotExist:
                return Response({
                    'detail': 'No assessment score found for this assessment'
                }, status=status.HTTP_404_NOT_FOUND)

            # Get all MCQ questions and scores for this assessment and student
            mcq_scores = MCQQuestionScore.objects.filter(
                question__assessment=assessment_score.assessment,
                enrollment=assessment_score.enrollment
            ).select_related('question')

            # Get all handwritten questions and scores
            handwritten_scores = HandwrittenQuestionScore.objects.filter(
                question__assessment=assessment_score.assessment,
                enrollment=assessment_score.enrollment
            ).select_related('question')

            # Get all Dynamic MCQ questions
            DynamicMCQ = apps.get_model('DynamicMCQ', 'DynamicMCQ')
            DynamicMCQQuestions = apps.get_model(
                'DynamicMCQ', 'DynamicMCQQuestions')

            # Get all Dynamic MCQ questions for this assessment
            dynamic_mcq = DynamicMCQ.objects.get(assessment=assessment)
            dynamic_mcq_questions = DynamicMCQQuestions.objects.filter(
                dynamic_mcq=dynamic_mcq,
                created_by=request.user
            )

            # Calculate total score of answered questions
            mcq_total = float(mcq_scores.aggregate(
                total=Sum('score'))['total'] or 0)
            handwritten_total = float(handwritten_scores.aggregate(
                total=Sum('score'))['total'] or 0)

            # Build questions data with student scores
            questions_data = []

            # Add MCQ questions
            for mcq_score in mcq_scores:
                question_data = {
                    'question_id': str(mcq_score.question.id),
                    'question_text': mcq_score.question.question,
                    'student_answer': mcq_score.selected_answer,
                    'is_correct': mcq_score.is_correct,
                    'score': str(mcq_score.score),
                    'max_score': str(mcq_score.question.question_grade),
                    'type': 'mcq'
                }

                if request.user.role in ['Teacher', 'Institution', 'Student']:
                    question_data.update({
                        'options': mcq_score.question.options,
                        'correct_answer': mcq_score.question.answer_key
                    })

                questions_data.append(question_data)

            # Add Handwritten questions
            for handwritten_score in handwritten_scores:
                question_data = {
                    'question_id': str(handwritten_score.question.id),
                    'question_text': handwritten_score.question.question_text,
                    'type': 'handwritten',
                    'score': str(handwritten_score.score),
                    'max_score': str(handwritten_score.question.max_grade),
                    'extracted_text': handwritten_score.extracted_text,
                    'feedback': handwritten_score.feedback,
                    'answer_image': request.build_absolute_uri(handwritten_score.answer_image.url) if handwritten_score.answer_image else None
                }

                if request.user.role in ['Teacher', 'Institution']:
                    question_data.update({
                        'correct_answer': handwritten_score.question.answer_key
                    })

                questions_data.append(question_data)

            # Add Dynamic MCQ questions
            dynamic_mcq_total = 0
            for question in dynamic_mcq_questions:
                # Get the score for this question from MCQQuestionScore using dynamic_question_id
                score = MCQQuestionScore.objects.filter(
                    dynamic_question_id=question.id,  # Match by dynamic_question_id
                    enrollment=assessment_score.enrollment
                ).first()

                if score:
                    dynamic_mcq_total += float(score.score)

                # Get the student's answer from the score's selected_answer field
                student_answer = score.selected_answer if score and hasattr(
                    score, 'selected_answer') else None

                question_data = {
                    'question_id': str(question.id),
                    'question_text': question.question,
                    'type': 'dynamic_mcq',
                    'max_score': str(question.question_grade),
                    'difficulty': question.difficulty,
                    'score': str(score.score) if score else '0',
                    'is_correct': score.is_correct if score else False,
                    'student_answer': student_answer
                }

                if request.user.role in ['Teacher', 'Institution', 'Student']:
                    question_data.update({
                        'options': question.options,
                        'correct_answer': question.answer_key
                    })

                questions_data.append(question_data)

            total_answered_score = mcq_total + handwritten_total + dynamic_mcq_total

            response_data = {
                'assessment_id': str(assessment_score.assessment.id),
                'assessment_title': assessment_score.assessment.title,
                'course': assessment_score.assessment.course.name,
                'questions': questions_data,
                'total_score': total_answered_score,
                'total_max_score': float(assessment_score.assessment.grade)
            }

            return Response(response_data)

        except Exception as e:
            return Response({
                'detail': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AssessmentAllQuestionsAPIView(generics.RetrieveAPIView):
    """
    API endpoint to get all questions for an assessment.

    This endpoint returns all questions (MCQ, Dynamic MCQ, and Handwritten) for an assessment
    based on the user's role.

    GET /api/assessments/{assessment_id}/all-questions/

    Parameters:
    - assessment_id (UUID): The ID of the assessment

    Returns:
    ```json
    {
        "assessment_id": "uuid",
        "assessment_title": "string",
        "questions": [
            {
                "id": "uuid",
                "type": "dynamic_mcq|mcq|handwritten",
                "question": "string",
                "options": ["string"],  // For MCQ and Dynamic MCQ
                "answer_key": "string",
                "difficulty": "string",  // For Dynamic MCQ
                "question_grade": "string",  // For MCQ
                "max_grade": "string",  // For Handwritten
                "created_by": "uuid"
            }
        ]
    }
    ```

    Status Codes:
    - 200: Successfully retrieved questions
    - 403: Not authorized to view questions
    - 404: Assessment not found
    """
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]
    serializer_class = AssessmentSerializer

    def get_object(self):
        try:
            return Assessment.objects.select_related('course').get(pk=self.kwargs['pk'])
        except Assessment.DoesNotExist:
            raise Http404("Assessment not found")

    def retrieve(self, request, *args, **kwargs):
        try:
            assessment = self.get_object()

            # Get all questions based on user role
            if request.user.role == "Student":
                # For students, only get their own questions
                mcq_questions = assessment.mcq_questions.filter(
                    assessment=assessment,
                    created_by=request.user
                )
                handwritten_questions = assessment.handwritten_questions.filter(
                    assessment=assessment,
                    created_by=request.user
                )
            else:
                # For teachers and institutions, get all questions
                mcq_questions = assessment.mcq_questions.all()
                handwritten_questions = assessment.handwritten_questions.all()

            # Get dynamic MCQs
            DynamicMCQ = apps.get_model('DynamicMCQ', 'DynamicMCQ')
            DynamicMCQQuestions = apps.get_model(
                'DynamicMCQ', 'DynamicMCQQuestions')
            dynamic_mcqs = DynamicMCQ.objects.filter(assessment=assessment)
            dynamic_questions = DynamicMCQQuestions.objects.filter(
                dynamic_mcq__in=dynamic_mcqs)

            # Prepare response data
            response_data = {
                'assessment_id': str(assessment.id),
                'assessment_title': assessment.title,
                'questions': []
            }

            # Add Dynamic MCQ questions
            for question in dynamic_questions:
                question_data = {
                    'id': str(question.id),
                    'type': 'dynamic_mcq',
                    'question': question.question_text,
                    'options': question.options,
                    'answer_key': question.answer_key,
                    'difficulty': question.difficulty,
                    'created_by': str(question.created_by.id) if question.created_by else None
                }
                response_data['questions'].append(question_data)

            # Add MCQ questions
            for question in mcq_questions:
                question_data = {
                    'id': str(question.id),
                    'type': 'mcq',
                    'question': question.question,
                    'options': question.options,
                    'answer_key': question.answer_key,
                    'question_grade': str(question.question_grade),
                    'created_by': str(question.created_by.id) if question.created_by else None
                }
                response_data['questions'].append(question_data)

            # Add Handwritten questions
            for question in handwritten_questions:
                question_data = {
                    'id': str(question.id),
                    'type': 'handwritten',
                    'question': question.question_text,
                    'answer_key': question.answer_key,
                    'max_grade': str(question.max_grade),
                    'created_by': str(question.created_by.id) if question.created_by else None
                }
                response_data['questions'].append(question_data)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AssessmentStudentQuestionsAPIView(generics.RetrieveAPIView):
    """
    API endpoint to get questions for a specific student in an assessment.

    This endpoint returns all questions (MCQ, Dynamic MCQ, and Handwritten) for a specific student
    in an assessment, including their section numbers and grades.

    GET /api/assessments/{assessment_id}/student-questions/

    Parameters:
    - assessment_id (UUID): The ID of the assessment

    Returns:
    ```json
    {
        "questions": [
            {
                "type": "dynamic_mcq|mcq|handwritten",
                "id": "uuid",
                "question": "string",
                "options": ["string"],  // For MCQ and Dynamic MCQ
                "grade": "string",  // For MCQ and Dynamic MCQ
                "max_grade": "string",  // For Handwritten
                "section_number": "integer"
            }
        ]
    }
    ```

    Status Codes:
    - 200: Successfully retrieved questions
    - 403: Not authorized to view questions
    - 404: Assessment not found
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssessmentSerializer

    def get_object(self):
        assessment_id = self.kwargs.get('pk')
        try:
            assessment = Assessment.objects.get(id=assessment_id)

            # Check if student is enrolled in the course
            if not Enrollments.objects.filter(
                user=self.request.user,
                course=assessment.course
            ).exists():
                raise PermissionDenied("You are not enrolled in this course")

            # Check if assessment is still accepting submissions
            if not assessment.accepting_submissions:
                raise PermissionDenied(
                    "This assessment is no longer accepting submissions")

            return assessment
        except Assessment.DoesNotExist:
            raise Http404("Assessment not found")

    def retrieve(self, request, *args, **kwargs):
        assessment = self.get_object()

        # Check if assessment has started
        if assessment.start_date > timezone.now():
            raise PermissionDenied(
                f"This assessment has not started yet. It will be available on {assessment.start_date.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Get all questions for the student
            questions = assessment.get_all_questions_for_student(request.user)

            # Format all questions into a single list with their types
            formatted_questions = []

            # Add dynamic MCQ questions
            formatted_questions.extend([
                {
                    'type': 'dynamic_mcq',
                    'id': str(q['id']),
                    'question': q['question'],
                    'options': q['options'],
                    'grade': q.get('grade', 0),
                    'section_number': q.get('section_number', 1)
                } for q in questions.get('dynamic_mcq', [])
            ])

            # Add regular MCQ questions
            formatted_questions.extend([
                {
                    'type': 'mcq',
                    'id': str(q['id']),
                    'question': q['question'],
                    'options': q['options'],
                    'grade': q.get('grade', 0),
                    'section_number': q.get('section_number', 1)
                } for q in questions.get('mcq', [])
            ])

            # Add handwritten questions
            formatted_questions.extend([
                {
                    'type': 'handwritten',
                    'id': str(q['id']),
                    'question': q['question'],
                    'max_grade': q.get('max_grade', 0),
                    'section_number': q.get('section_number', 1)
                } for q in questions.get('handwritten', [])
            ])

            # Sort questions by section number
            formatted_questions.sort(key=lambda x: x['section_number'])

            # Add assessment details
            response_data = {
                'assessment': {
                    'id': str(assessment.id),
                    'title': assessment.title,
                    'type': assessment.type,
                    'due_date': assessment.due_date,
                    'grade': assessment.grade,
                    'total_grade': assessment.total_grade,
                    'course': assessment.course.name
                },
                'questions': formatted_questions
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
