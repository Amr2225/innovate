from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import DynamicMCQ, DynamicMCQQuestions
from .serializers import DynamicMCQSerializer, DynamicMCQQuestionsSerializer
from assessment.models import Assessment
from users.models import User
from rest_framework.exceptions import PermissionDenied

# Create your views here.

class DynamicMCQPermission(permissions.BasePermission):
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
        
        # Students can only view their own MCQs
        if request.user.role == "Student":
            return obj.assessment.course.enrollments.filter(user=request.user).exists()
        
        # Teachers can access MCQs for their courses
        if request.user.role == "Teacher":
            return obj.assessment.course.instructors.filter(id=request.user.id).exists()
        
        # Institutions can access MCQs for their courses
        if request.user.role == "Institution":
            return obj.assessment.course.institution == request.user
        
        return False

class DynamicMCQListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DynamicMCQSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicMCQPermission]

    def get_queryset(self):
        user = self.request.user
        assessment_id = self.kwargs.get('assessment_id')
        
        if user.role == "Student":
            # Students can only see MCQs for courses they're enrolled in
            return DynamicMCQ.objects.filter(
                assessment_id=assessment_id,
                assessment__course__enrollments__user=user
            ).distinct()
        elif user.role == "Teacher":
            # Teachers can see MCQs for their courses
            return DynamicMCQ.objects.filter(
                assessment_id=assessment_id,
                assessment__course__instructors=user
            )
        elif user.role == "Institution":
            # Institutions can see MCQs for their courses
            return DynamicMCQ.objects.filter(
                assessment_id=assessment_id,
                assessment__course__institution=user
            )
        
        return DynamicMCQ.objects.none()

    def perform_create(self, serializer):
        assessment_id = self.kwargs.get('assessment_id')
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            
            # Check if user has permission to create MCQ for this assessment
            if self.request.user.role == "Teacher":
                if not assessment.course.instructors.filter(id=self.request.user.id).exists():
                    raise PermissionDenied("You don't have permission to create MCQs for this assessment")
            elif self.request.user.role == "Institution":
                if assessment.course.institution != self.request.user:
                    raise PermissionDenied("You don't have permission to create MCQs for this assessment")
            else:
                raise PermissionDenied("Only teachers and institutions can create MCQs")
            
            serializer.save(assessment=assessment)
        except Assessment.DoesNotExist:
            raise PermissionDenied("Assessment not found")

class DynamicMCQDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DynamicMCQSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicMCQPermission]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "Student":
            # Students can only see MCQs for courses they're enrolled in
            return DynamicMCQ.objects.filter(
                assessment__course__enrollments__user=user
            ).distinct()
        elif user.role == "Teacher":
            # Teachers can see MCQs for their courses
            return DynamicMCQ.objects.filter(
                assessment__course__instructors=user
            )
        elif user.role == "Institution":
            # Institutions can see MCQs for their courses
            return DynamicMCQ.objects.filter(
                assessment__course__institution=user
            )
        
        return DynamicMCQ.objects.none()

class DynamicMCQQuestionsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DynamicMCQQuestionsSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicMCQPermission]

    def get_queryset(self):
        dynamic_mcq_id = self.kwargs.get('dynamic_mcq_id')
        user = self.request.user
        
        if user.role == "Student":
            # Students can only see questions for MCQs in courses they're enrolled in
            return DynamicMCQQuestions.objects.filter(
                dynamic_mcq_id=dynamic_mcq_id,
                dynamic_mcq__assessment__course__enrollments__user=user
            ).distinct()
        elif user.role == "Teacher":
            # Teachers can see questions for their MCQs
            return DynamicMCQQuestions.objects.filter(
                dynamic_mcq_id=dynamic_mcq_id,
                dynamic_mcq__assessment__course__instructors=user
            )
        elif user.role == "Institution":
            # Institutions can see questions for their MCQs
            return DynamicMCQQuestions.objects.filter(
                dynamic_mcq_id=dynamic_mcq_id,
                dynamic_mcq__assessment__course__institution=user
            )
        
        return DynamicMCQQuestions.objects.none()

    def perform_create(self, serializer):
        dynamic_mcq_id = self.kwargs.get('dynamic_mcq_id')
        try:
            dynamic_mcq = DynamicMCQ.objects.get(id=dynamic_mcq_id)
            
            # Check if user has permission to create questions for this MCQ
            if self.request.user.role == 'teacher':
                if dynamic_mcq.assessment.course.teacher != self.request.user.teacher:
                    raise PermissionDenied("You don't have permission to create questions for this MCQ")
            elif self.request.user.role == 'institution':
                if dynamic_mcq.assessment.course.institution != self.request.user.institution:
                    raise PermissionDenied("You don't have permission to create questions for this MCQ")
            else:
                raise PermissionDenied("Only teachers and institutions can create questions")
            
            serializer.save(dynamic_mcq=dynamic_mcq)
        except DynamicMCQ.DoesNotExist:
            raise PermissionDenied("Dynamic MCQ not found")

class DynamicMCQQuestionsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DynamicMCQQuestionsSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicMCQPermission]

    def get_queryset(self):
        dynamic_mcq_id = self.kwargs.get('dynamic_mcq_id')
        user = self.request.user
        
        if user.role == "Student":
            # Students can only see questions for MCQs in courses they're enrolled in
            return DynamicMCQQuestions.objects.filter(
                dynamic_mcq_id=dynamic_mcq_id,
                dynamic_mcq__assessment__course__enrollments__user=user
            ).distinct()
        elif user.role == "Teacher":
            # Teachers can see questions for their MCQs
            return DynamicMCQQuestions.objects.filter(
                dynamic_mcq_id=dynamic_mcq_id,
                dynamic_mcq__assessment__course__instructors=user
            )
        elif user.role == "Institution":
            # Institutions can see questions for their MCQs
            return DynamicMCQQuestions.objects.filter(
                dynamic_mcq_id=dynamic_mcq_id,
                dynamic_mcq__assessment__course__institution=user
            )
        
        return DynamicMCQQuestions.objects.none()
