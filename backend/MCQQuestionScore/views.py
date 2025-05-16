from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from .models import MCQQuestionScore
from .serializers import MCQQuestionScoreSerializer
from users.permissions import isStudent, isTeacher, isInstitution
from mcqQuestion.models import McqQuestion
from assessment.models import Assessment, AssessmentScore
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Sum
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

class MCQQuestionScorePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return request.user.role == "Student"
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if request.method in permissions.SAFE_METHODS:
            if user.role == "Student":
                return obj.student == user
            elif user.role in ["Teacher", "Institution"]:
                return (obj.question.assessment.course.instructors.filter(id=user.id).exists() or
                        obj.question.assessment.course.institution == user)
        return False

class MCQQuestionScoreListCreateView(generics.ListCreateAPIView):
    serializer_class = MCQQuestionScoreSerializer
    permission_classes = [MCQQuestionScorePermission]

    def get_queryset(self):
        user = self.request.user
        base_queryset = MCQQuestionScore.objects.select_related(
            'question__assessment__course',
            'student'
        )

        # Filter by assessment if provided
        assessment_id = self.request.query_params.get('assessment_id')
        if assessment_id:
            try:
                Assessment.objects.get(id=assessment_id)
                base_queryset = base_queryset.filter(question__assessment_id=assessment_id)
            except (ValidationError, ObjectDoesNotExist):
                return MCQQuestionScore.objects.none()

        if user.role == "Student":
            return base_queryset.filter(student=user)
        elif user.role == "Teacher":
            return base_queryset.filter(
                question__assessment__course__instructors=user
            )
        elif user.role == "Institution":
            return base_queryset.filter(
                question__assessment__course__institution=user
            )
        return MCQQuestionScore.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "Student":
            raise PermissionDenied("Only students can submit answers")

        # Get the question instance
        question_id = self.request.data.get('question')
        try:
            question = McqQuestion.objects.select_related('assessment__course').get(id=question_id)
        except (McqQuestion.DoesNotExist, ValidationError):
            raise ValidationError({"question": "Question does not exist"})

        # Validate course enrollment
        if not question.assessment.course.enrollments.filter(user=user).exists():
            raise PermissionDenied("You are not enrolled in this course")

        # Check if assessment is active and accepting submissions
        assessment = question.assessment
        if not assessment.is_active:
            raise ValidationError({"detail": "This assessment is not active"})
        if assessment.due_date < timezone.now():
            raise ValidationError({"detail": "This assessment is past due"})
        if not assessment.accepting_submissions:
            raise ValidationError({"detail": "This assessment is not accepting submissions"})

        # Validate selected answer is one of the options
        selected_answer = self.request.data.get('selected_answer')
        if not selected_answer:
            raise ValidationError({"selected_answer": "This field is required"})

        if selected_answer not in question.answer:
            raise ValidationError({"selected_answer": "Selected answer must be one of the provided options"})

        try:
            with transaction.atomic():
                # Update or create the score
                score, created = MCQQuestionScore.objects.update_or_create(
                    student=user,
                    question=question,
                    defaults={
                        'selected_answer': selected_answer,
                        'is_correct': selected_answer == question.answer_key,
                        'score': question.question_grade if selected_answer == question.answer_key else 0
                    }
                )

                # Update or create AssessmentScore
                assessment_score, created = AssessmentScore.objects.update_or_create(
                    student=user,
                    assessment=assessment,
                    defaults={'total_score': assessment.get_student_score(user)}
                )

                return score
        except Exception as e:
            raise ValidationError({"detail": f"Error saving score: {str(e)}"})

    def create(self, request, *args, **kwargs):
        try:
            # Add student to serializer context
            serializer = self.get_serializer(data=request.data)
            serializer.context['student'] = request.user
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            if request.user.role == 'Student':
                return Response({
                    'message': 'student submits his answer successfully'
                }, status=status.HTTP_201_CREATED, headers=headers)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class MCQQuestionScoreDetailView(generics.RetrieveAPIView):
    serializer_class = MCQQuestionScoreSerializer
    permission_classes = [MCQQuestionScorePermission]

    def get_queryset(self):
        user = self.request.user
        base_queryset = MCQQuestionScore.objects.select_related(
            'question__assessment__course',
            'student'
        )

        if user.role == "Student":
            return base_queryset.filter(student=user)
        elif user.role == "Teacher":
            return base_queryset.filter(
                question__assessment__course__instructors=user
            )
        elif user.role == "Institution":
            return base_queryset.filter(
                question__assessment__course__institution=user
            )
        return MCQQuestionScore.objects.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Add additional context for teachers/institutions
        if request.user.role in ["Teacher", "Institution"]:
            data.update({
                'student_name': f"{instance.student.first_name} {instance.student.last_name}",
                'student_email': instance.student.email,
                'assessment_title': instance.question.assessment.title,
                'course_name': instance.question.assessment.course.name
            })
            
        return Response(data)

class MCQQuestionScoreBulkView(generics.CreateAPIView):
    serializer_class = MCQQuestionScoreSerializer
    permission_classes = [MCQQuestionScorePermission]

    def create(self, request, *args, **kwargs):
        if request.user.role != "Student":
            raise PermissionDenied("Only students can submit answers")

        answers = request.data.get('answers', [])
        if not isinstance(answers, list):
            raise ValidationError({"answers": "Answers must be a list"})

        assessment_id = request.data.get('assessment_id')
        if not assessment_id:
            raise ValidationError({"assessment_id": "Assessment ID is required"})

        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            raise ValidationError({"assessment_id": "Assessment not found"})

        # Validate course enrollment
        if not assessment.course.enrollments.filter(user=request.user).exists():
            raise PermissionDenied("You are not enrolled in this course")

        # Validate assessment status
        if not assessment.is_active:
            raise ValidationError({"detail": "This assessment is not active"})
        if assessment.due_date < timezone.now():
            raise ValidationError({"detail": "This assessment is past due"})
        if not assessment.accepting_submissions:
            raise ValidationError({"detail": "This assessment is not accepting submissions"})

        results = []
        with transaction.atomic():
            for answer in answers:
                question_id = answer.get('question_id')
                selected_answer = answer.get('selected_answer')

                if not question_id or not selected_answer:
                    raise ValidationError("Each answer must include question_id and selected_answer")

                try:
                    question = McqQuestion.objects.get(
                        id=question_id,
                        assessment=assessment
                    )
                except McqQuestion.DoesNotExist:
                    raise ValidationError(f"Question {question_id} not found or not part of this assessment")

                # Validate selected answer
                if selected_answer not in question.answer:
                    raise ValidationError(f"Invalid answer for question {question_id}")

                # Create or update score
                score, created = MCQQuestionScore.objects.update_or_create(
                    question=question,
                    student=request.user,
                    defaults={
                        'selected_answer': selected_answer,
                        'is_correct': selected_answer == question.answer_key,
                        'score': question.question_grade if selected_answer == question.answer_key else 0
                    }
                )

                results.append({
                    'question_id': str(question_id),
                    'is_correct': score.is_correct,
                    'score': str(score.score)
                })

            # Update assessment score
            AssessmentScore.objects.update_or_create(
                student=request.user,
                assessment=assessment,
                defaults={'total_score': assessment.get_student_score(request.user)}
            )

        return Response({
            'message': 'Answers submitted successfully',
            'results': results,
            'total_score': str(assessment.get_student_score(request.user))
        }, status=status.HTTP_201_CREATED)
