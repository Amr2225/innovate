from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import Assessment, AssessmentScore, AssessmentSubmission
from .serializers import AssessmentSerializer, AssessmentScoreSerializer, AssessmentSubmissionSerializer
from courses.models import Course
from enrollments.models import Enrollments
from mcqQuestion.models import McqQuestion
from mcqQuestion.serializers import McqQuestionSerializer
from MCQQuestionScore.models import MCQQuestionScore
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.db import transaction
from django.shortcuts import get_object_or_404

# ----------------------
# Assessment Views
# ----------------------

class AssessmentPermission(permissions.BasePermission):
    """Custom permission class for assessments"""
    
    def has_permission(self, request, view):
        # Anyone authenticated can view
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Teachers and institutions can create/update/delete
        return request.user.role in ["Teacher", "Institution"]
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        # For read operations
        if request.method in permissions.SAFE_METHODS:
            if user.role == "Student":
                # Students can only view assessments for courses they're enrolled in
                is_completed = request.query_params.get('is_completed', 'false').lower() == 'true'
                return Enrollments.objects.filter(
                    user=user,
                    course=obj.course,
                    is_completed=is_completed
                ).exists()
            elif user.role == "Teacher":
                # Teachers can view assessments for courses they teach
                return obj.course.instructors.filter(id=user.id).exists()
            elif user.role == "Institution":
                # Institution can view any assessment in their courses
                return obj.course.institution == user
            return False

        # For write operations (create/update/delete)
        if user.role == "Teacher":
            # Teachers can modify assessments for courses they teach
            return obj.course.instructors.filter(id=user.id).exists()
        elif user.role == "Institution":
            # Institution can modify any assessment in their courses
            return obj.course.institution == user
        return False

class AssessmentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [AssessmentPermission]
    filterset_fields = ['due_date', 'type', 'title']

    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            # Institution can see all assessments in their courses
            return Assessment.objects.filter(course__institution=user)
        elif user.role == "Teacher":
            # Teachers can see assessments for courses they teach
            return Assessment.objects.filter(course__instructors=user)
        elif user.role == "Student":
            # Students can only see assessments for courses they're enrolled in
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return Assessment.objects.filter(course__id__in=enrolled_courses)
        return Assessment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        course = Course.objects.get(id=self.request.data.get('course'))
        
        # Check permissions based on role
        if user.role == "Teacher" and not course.instructors.filter(id=user.id).exists():
            raise PermissionDenied("You are not an instructor for this course")
        elif user.role == "Institution" and course.institution != user:
            raise PermissionDenied("This course does not belong to your institution")
            
        serializer.save()

class AssessmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [AssessmentPermission]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            # Institution can access any assessment in their courses
            return Assessment.objects.filter(course__institution=user)
        elif user.role == "Teacher":
            # Teachers can access assessments for courses they teach
            return Assessment.objects.filter(course__instructors=user)
        elif user.role == "Student":
            # Students can only access assessments for courses they're enrolled in
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return Assessment.objects.filter(course__id__in=enrolled_courses)
        return Assessment.objects.none()

# ----------------------
# Assessment Score Views
# ----------------------

class AssessmentScoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['assessment']

    def get_queryset(self):
        user = self.request.user
        queryset = AssessmentScore.objects.all()

        # Filter by assessment_id if provided
        assessment_id = self.request.query_params.get('assessment_id')
        if assessment_id:
            queryset = queryset.filter(assessment_id=assessment_id)

        # Filter by enrollment_id if provided
        enrollment_id = self.request.query_params.get('enrollment_id')
        if enrollment_id:
            queryset = queryset.filter(enrollment_id=enrollment_id)

        if user.role == "Institution":
            return queryset.filter(assessment__course__institution=user)
        elif user.role == "Teacher":
            return queryset.filter(assessment__course__instructors=user)
        elif user.role == "Student":
            # Students can only see their own scores for enrolled courses
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            enrollments = Enrollments.objects.filter(user=user, course__id__in=enrolled_courses)
            return queryset.filter(
                assessment__course__id__in=enrolled_courses,
                enrollment__in=enrollments
            )
        return AssessmentScore.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "Student":
            raise PermissionDenied("Only students can submit assessment scores")

        assessment = Assessment.objects.get(id=self.request.data.get('assessment'))
        
        # Check if the assessment is still accepting submissions
        if not assessment.accepting_submissions:
            raise PermissionDenied("This assessment is no longer accepting submissions as it has passed its due date")
        
        # Check if student is enrolled in the course
        is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
        if not Enrollments.objects.filter(
            user=user,
            course=assessment.course,
            is_completed=is_completed
        ).exists():
            raise PermissionDenied("You are not enrolled in this course")
        
        enrollment = Enrollments.objects.get(user=user, course=assessment.course)
        # Check if student has already submitted
        if AssessmentScore.objects.filter(assessment=assessment, enrollment=enrollment).exists():
            raise PermissionDenied("You have already submitted this assessment")
        
        serializer.save(enrollment=enrollment)

class AssessmentScoreRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = AssessmentScore.objects.all()

        # Filter by assessment_id if provided
        assessment_id = self.request.query_params.get('assessment_id')
        if assessment_id:
            queryset = queryset.filter(assessment_id=assessment_id)

        # Filter by enrollment_id if provided
        enrollment_id = self.request.query_params.get('enrollment_id')
        if enrollment_id:
            queryset = queryset.filter(enrollment_id=enrollment_id)

        if user.role == "Institution":
            return queryset.filter(assessment__course__institution=user)
        elif user.role == "Teacher":
            return queryset.filter(assessment__course__instructors=user)
        elif user.role == "Student":
            # Students can only access their own scores for enrolled courses
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            enrollments = Enrollments.objects.filter(user=user, course__id__in=enrolled_courses)
            return queryset.filter(
                assessment__course__id__in=enrolled_courses,
                enrollment__in=enrollments
            )
        return AssessmentScore.objects.none()

class AssessmentQuestionsAPIView(generics.ListAPIView):
    """View to get all questions for a specific assessment"""
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
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
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
    """View to get total grade for a student's assessment"""
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        try:
            enrollment_id = request.data.get('enrollment_id')
            assessment_id = request.data.get('assessment_id')

            if not enrollment_id or not assessment_id:
                return Response({
                    'detail': 'Both enrollment_id and assessment_id are required in request body'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the assessment score
            try:
                assessment_score = AssessmentScore.objects.select_related(
                    'assessment__course',
                    'enrollment__user'
                ).get(
                    enrollment_id=enrollment_id,
                    assessment_id=assessment_id
                )
            except AssessmentScore.DoesNotExist:
                return Response({
                    'detail': 'No assessment score found for this Student and assessment'
                }, status=status.HTTP_404_NOT_FOUND)

            # Check permissions
            user = request.user
            if user.role == "Student" and str(assessment_score.enrollment.user.id) != str(user.id):
                return Response({
                    'detail': 'You can only view your own grades'
                }, status=status.HTTP_403_FORBIDDEN)
            elif user.role == "Teacher" and not assessment_score.assessment.course.instructors.filter(id=user.id).exists():
                return Response({
                    'detail': 'You can only view grades for your courses'
                }, status=status.HTTP_403_FORBIDDEN)
            elif user.role == "Institution" and assessment_score.assessment.course.institution != user:
                return Response({
                    'detail': 'You can only view grades for your institution'
                }, status=status.HTTP_403_FORBIDDEN)

            # Get all MCQ questions and scores for this assessment and student
            mcq_scores = MCQQuestionScore.objects.filter(
                question__assessment=assessment_score.assessment,
                enrollment=assessment_score.enrollment
            ).select_related('question')

            # Calculate total score of answered questions
            total_answered_score = mcq_scores.aggregate(total=Sum('score'))['total'] or 0

            # Build questions data with student scores
            questions_data = []
            for mcq_score in mcq_scores:
                question_data = {
                    'question_id': str(mcq_score.question.id),
                    'question_text': mcq_score.question.question,
                    'student_answer': mcq_score.selected_answer,
                    'is_correct': mcq_score.is_correct,
                    'score': str(mcq_score.score),
                    'max_score': str(mcq_score.question.question_grade)
                }
                
                if user.role in ['Teacher', 'Institution','Student']:
                    question_data.update({
                        'options': mcq_score.question.answer,
                        'correct_answer': mcq_score.question.answer_key
                    })
                
                questions_data.append(question_data)

            response_data = {
                'assessment_id': str(assessment_score.assessment.id),
                'assessment_title': assessment_score.assessment.title,
                'enrollment_id': str(assessment_score.enrollment.id),
                'student_name': f"{assessment_score.enrollment.user.first_name} {assessment_score.enrollment.user.last_name}",
                'questions': questions_data,
                'total_score': int(total_answered_score),
                'total_max_score': int(assessment_score.assessment.grade)
            }

            return Response(response_data)

        except Exception as e:
            return Response({
                'detail': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AssessmentAllQuestionsAPIView(generics.RetrieveAPIView):
    """API view to get all questions for an assessment"""
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]
    serializer_class = AssessmentSerializer

    def get_object(self):
        return get_object_or_404(Assessment, pk=self.kwargs['pk'])

    def retrieve(self, request, *args, **kwargs):
        assessment = self.get_object()
        
        # Get all questions
        mcq_questions = assessment.mcq_questions.all()
        handwritten_questions = assessment.handwritten_questions.all()
        
        # Get student's submission if they are a student
        student_submission = None
        if request.user.role == 'Student':
            try:
                enrollment = Enrollments.objects.get(
                    user=request.user,
                    course=assessment.course,
                    is_active=True
                )
                student_submission = AssessmentSubmission.objects.get(
                    assessment=assessment,
                    enrollment=enrollment
                )
            except (Enrollments.DoesNotExist, AssessmentSubmission.DoesNotExist):
                pass

        # Format MCQ questions
        mcq_data = []
        for question in mcq_questions:
            mcq_dict = {
                'id': str(question.id),
                'type': 'mcq',
                'question_text': question.question_text,
                'options': question.options,
                'question_grade': question.question_grade
            }
            
            # Add answer key for teachers and institutions
            if request.user.role in ['Teacher', 'Institution']:
                mcq_dict['answer_key'] = question.answer_key
            
            # Add student's answer if available
            if student_submission:
                student_answer = student_submission.mcq_answers.get(str(question.id))
                if student_answer:
                    mcq_dict['student_answer'] = {
                        'selected_answer': student_answer,
                        'is_correct': student_answer == question.answer_key,
                        'score': question.question_grade if student_answer == question.answer_key else 0
                    }
            
            mcq_data.append(mcq_dict)

        # Format Handwritten questions
        handwritten_data = []
        for question in handwritten_questions:
            handwritten_dict = {
                'id': str(question.id),
                'type': 'handwritten',
                'question_text': question.question_text,
                'max_grade': question.max_grade
            }
            
            # Add answer key for teachers and institutions
            if request.user.role in ['Teacher', 'Institution']:
                handwritten_dict['answer_key'] = question.answer_key
            
            # Add student's answer if available
            if student_submission:
                from HandwrittenQuestion.models import HandwrittenQuestionScore
                try:
                    score = HandwrittenQuestionScore.objects.get(
                        question=question,
                        enrollment=student_submission.enrollment
                    )
                    handwritten_dict['student_answer'] = {
                        'image_url': request.build_absolute_uri(score.answer_image.url) if score.answer_image else None,
                        'extracted_text': score.extracted_text,
                        'feedback': score.feedback,
                        'score': score.score
                    }
                except HandwrittenQuestionScore.DoesNotExist:
                    pass
            
            handwritten_data.append(handwritten_dict)

        # Combine all questions
        all_questions = mcq_data + handwritten_data

        response_data = {
            'assessment_id': str(assessment.id),
            'assessment_title': assessment.title,
            'total_questions': len(all_questions),
            'mcq_count': len(mcq_data),
            'handwritten_count': len(handwritten_data),
            'questions': all_questions
        }

        return Response(response_data)

class AssessmentSubmissionAPIView(generics.CreateAPIView):
    """View to submit all answers for an assessment"""
    serializer_class = AssessmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, *args, **kwargs):
        """Get all students' answers for an assessment"""
        try:
            assessment_id = kwargs.get('pk')
            assessment = Assessment.objects.get(id=assessment_id)
            user = request.user

            # Check permissions
            if user.role == "Student":
                # Students can only view their own submissions
                is_completed = request.query_params.get('is_completed', 'false').lower() == 'true'
                submissions = AssessmentSubmission.objects.filter(
                    assessment=assessment,
                    enrollment__user=user,
                    enrollment__is_completed=is_completed
                )
            elif user.role == "Teacher":
                # Teachers can view submissions for courses they teach
                if not assessment.course.instructors.filter(id=user.id).exists():
                    return Response(
                        {"detail": "You don't have permission to view these submissions"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                submissions = AssessmentSubmission.objects.filter(assessment=assessment)
            elif user.role == "Institution":
                # Institution can view all submissions for their courses
                if assessment.course.institution != user:
                    return Response(
                        {"detail": "You don't have permission to view these submissions"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                submissions = AssessmentSubmission.objects.filter(assessment=assessment)
            else:
                return Response(
                    {"detail": "You don't have permission to view these submissions"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get all questions
            mcq_questions = assessment.mcq_questions.all()
            handwritten_questions = assessment.handwritten_questions.all()

            # Prepare response data
            response_data = {
                'assessment_id': str(assessment.id),
                'assessment_title': assessment.title,
                'total_submissions': submissions.count(),
                'questions': {
                    'mcq': [],
                    'handwritten': []
                },
                'submissions': []
            }

            # Add MCQ questions with answer keys
            for question in mcq_questions:
                question_data = {
                    'id': str(question.id),
                    'question': question.question,
                    'options': question.answer,
                    'answer_key': question.answer_key if user.role in ['Teacher', 'Institution','Student'] else None,
                    'question_grade': str(question.question_grade)
                }
                response_data['questions']['mcq'].append(question_data)

            # Add Handwritten questions with answer keys
            for question in handwritten_questions:
                question_data = {
                    'id': str(question.id),
                    'question': question.question_text,
                    'answer_key': question.answer_key if user.role in ['Teacher', 'Institution','Student'] else None,
                    'max_grade': str(question.max_grade)
                }
                response_data['questions']['handwritten'].append(question_data)

            # Add submissions with answers
            for submission in submissions:
                submission_data = {
                    'submission_id': str(submission.id),
                    'student_email': submission.enrollment.user.email,
                    'submitted_at': submission.submitted_at,
                    'answers': {
                        'mcq': {},
                        'handwritten': {}
                    }
                }

                # Add MCQ answers
                for question_id, answer in submission.mcq_answers.items():
                    question = mcq_questions.filter(id=question_id).first()
                    if question:
                        submission_data['answers']['mcq'][question_id] = {
                            'selected_answer': answer,
                            'is_correct': answer == question.answer_key if user.role in ['Teacher', 'Institution','Student'] else None
                        }

                # Add Handwritten answers
                for question_id, image_path in submission.handwritten_answers.items():
                    question = handwritten_questions.filter(id=question_id).first()
                    if question:
                        # Get the score record for this answer
                        from HandwrittenQuestion.models import HandwrittenQuestionScore
                        score = HandwrittenQuestionScore.objects.filter(
                            question_id=question_id,
                            enrollment=submission.enrollment
                        ).first()
                        
                        submission_data['answers']['handwritten'][question_id] = {
                            'image_url': request.build_absolute_uri(score.answer_image.url) if score and score.answer_image else None,
                            'extracted_text': score.extracted_text if score else None,
                            'score': str(score.score) if score else None,
                            'feedback': score.feedback if score else None
                        }

                response_data['submissions'].append(submission_data)

            return Response(response_data)

        except Assessment.DoesNotExist:
            return Response(
                {"detail": "Assessment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            assessment_id = kwargs.get('pk')
            assessment = Assessment.objects.get(id=assessment_id)

            # Get the enrollment
            is_completed = request.query_params.get('is_completed', 'false').lower() == 'true'
            enrollment = Enrollments.objects.get(
                user=request.user,
                course=assessment.course,
                is_completed=is_completed
            )

            # Check if already submitted
            if AssessmentSubmission.objects.filter(
                assessment=assessment,
                enrollment=enrollment,
                is_submitted=True
            ).exists():
                return Response(
                    {"detail": "You have already submitted this assessment"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process MCQ answers
            mcq_answers = {}
            for question_id, answer in request.data.get('mcq_answers', {}).items():
                mcq_answers[str(question_id)] = answer

            # Process Handwritten answers
            handwritten_answers = {}
            for question_id, image in request.FILES.items():
                if question_id.startswith('handwritten_'):
                    question_id = question_id.replace('handwritten_', '')
                    # Save the image and get its path
                    from HandwrittenQuestion.models import HandwrittenQuestionScore
                    score = HandwrittenQuestionScore(
                        question_id=question_id,
                        enrollment=enrollment,
                        answer_image=image
                    )
                    score.save()
                    handwritten_answers[str(question_id)] = score.answer_image.path

            # Create submission
            with transaction.atomic():
                submission = AssessmentSubmission.objects.create(
                    assessment=assessment,
                    enrollment=enrollment,
                    mcq_answers=mcq_answers,
                    handwritten_answers=handwritten_answers,
                    is_submitted=True
                )

                # The save method will handle creating scores and updating assessment score
                submission.save()

            return Response({
                "message": "Assessment submitted successfully",
                "submission_id": str(submission.id)
            }, status=status.HTTP_201_CREATED)

        except Assessment.DoesNotExist:
            return Response(
                {"detail": "Assessment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Enrollments.DoesNotExist:
            return Response(
                {"detail": "You are not enrolled in this course"},
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
