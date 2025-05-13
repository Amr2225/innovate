from courses.serializers import CourseSerializer
from courses.models import Course
from enrollments.models import Enrollments
from users.models import User
from rest_framework import generics
from users.permissions import isInstitution, isStudent, isTeacher
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
import csv


class CourseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    filterset_fields = ['id', 'name', 'description', 'prerequisite_course', 'instructors', 'total_grade', 'credit_hours', 'semester']

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "Institution":
            return Course.objects.filter(institution_id=user.id)
        elif user.role == "Teacher":
            return Course.objects.filter(instructors=user)
        elif user.role == "Student":
            enrolled_course_ids = Enrollments.objects.filter(
                user=user
            ).values_list('course_id', flat=True)
            return Course.objects.filter(id__in=enrolled_course_ids)
        return Course.objects.none()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            self.permission_classes = [isInstitution]
        return super().get_permissions()


class RetrieveUpdateDestroyCourseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_url_kwarg = 'p_id'

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [isInstitution]
        return super().get_permissions()


class CourseProgressListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return []

    def list(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        try:
            course = Course.objects.get(id=course_id)
            
            # Check if user has access to this course
            user = request.user
            if user.role == "Student":
                if not Enrollments.objects.filter(user=user, course=course).exists():
                    raise PermissionDenied("You are not enrolled in this course.")
            elif user.role == "Teacher":
                if not course.instructors.filter(id=user.id).exists():
                    raise PermissionDenied("You are not an instructor of this course.")
            elif user.role != "Institution" or course.institution != user:
                raise PermissionDenied("You don't have access to this course.")
            
            progress = course.get_user_course_progress(request.user)
            return Response({"course_progress": progress})
        except Course.DoesNotExist:
            raise NotFound("Course not found.")

class BulkCourseImportView(APIView):
    permission_classes = [isInstitution]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        excel_file = request.FILES.get('file')
        if not excel_file or not excel_file.name.endswith(('.csv')):
            return Response({"error": "Please upload a valid CSV file"}, status=400)

        try:
            decoded_file = excel_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            created, errors = [], []

            for row in reader:
                if row['prerequisite_course'] and row['prerequisite_course'].lower() != "none":
                    prerequisite_course = Course.objects.filter(name=row['prerequisite_course']).first()
                    if prerequisite_course:
                        row['prerequisite_course'] = prerequisite_course.id
                    else:
                        row['prerequisite_course'] = None
                else:
                    row['prerequisite_course'] = None

                if row['instructors']:
                    instructor_names = row['instructors'].strip("[]").split(',')
                    instructor_ids = []
                    for instructor_name in instructor_names:
                        names = instructor_name.strip().split()
                        if len(names) >= 2:
                            first_name, last_name = names[0], names[1]
                            instructor = User.objects.filter(first_name=first_name, last_name=last_name).first()
                            if instructor:
                                instructor_ids.append(instructor.id)
                            else:
                                errors.append({"row": row, "error": f"Instructor {instructor_name} not found"})
                        else:
                            errors.append({"row": row, "error": f"Invalid instructor name format: {instructor_name}"})

                    row['instructors'] = instructor_ids
                else:
                    row['instructors'] = []

                row["institution"] = request.user.id

                serializer = CourseSerializer(data=row, context={"request": request})

                if serializer.is_valid():
                    serializer.save()
                    created.append(serializer.data)
                else:
                    errors.append({"row": row, "errors": serializer.errors})

            return Response({"created": created, "errors": errors}, status=201 if not errors else 400)

        except Exception as e:
            return Response({"error": str(e)}, status=400)