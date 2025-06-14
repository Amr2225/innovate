from rest_framework import serializers
from chapter.models import Chapter
from enrollments.models import Enrollments
from lecture.serializers import LectureSerializer
from lecture.models import Lecture
from courses.models import Course


class ChapterSerializer(serializers.ModelSerializer):
    # lecture_details = LectureSerializer(
    #     source='lectures', many=True, read_only=True)
    lectures = LectureSerializer(many=True, read_only=True)
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True
    )

    class Meta:
        model = Chapter
        fields = ('id', 'title', 'lectures', 'course')
        extra_kwargs = {
            'lectures': {'read_only': True, 'required': False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.role == "Institution":
            self.fields['course'].queryset = Course.objects.filter(
                institution=request.user)


# TODO: Move this to lecture app
class LectureCreateSerializer(serializers.ModelSerializer):
    video = serializers.FileField(required=False, allow_null=True)
    attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Lecture
        fields = ('title', 'description', "video", "attachment")


class ChapterWithLecturesSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    courseId = serializers.UUIDField()
    lectures = LectureCreateSerializer(many=True, required=False)

    def validate_courseId(self, value):
        try:
            course = Course.objects.get(id=value)
            request = self.context.get('request')
            user = request.user

            if user.role == "Institution" and course.institution != user:
                raise serializers.ValidationError(
                    f"You do not have permission to add a chapter to course: {course.name}")

            elif user.role == "Teacher" and course.institution not in user.institution.all():
                raise serializers.ValidationError(
                    f"You do not have permission to add a chapter to course: {course.name}")

            return course
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course does not exist")


class ChapterBulkCreateSerializer(serializers.Serializer):
    chapters = serializers.ListField(
        child=ChapterWithLecturesSerializer(),
        min_length=1,
        required=True,
        error_messages={
            'required': 'A list of chapters is required for bulk creation.',
            'empty': 'At least one chapter must be provided for bulk creation.',
            'invalid': 'Invalid data format. Expected a list of chapter objects.'
        }
    )

    def create(self, validated_data):
        chapters_data = validated_data.get('chapters')
        created_chapters = []

        for chapter_data in chapters_data:
            course = chapter_data.pop('courseId')
            lectures_data = chapter_data.pop('lectures', [])

            # Create chapter
            chapter = Chapter.objects.create(
                title=chapter_data['title'],
                course=course
            )

            # Create lectures for this chapter
            for lecture_data in lectures_data:
                # Handle file uploads
                lecture = Lecture(chapter=chapter)

                # Set basic fields
                lecture.title = lecture_data.get('title', '')
                lecture.description = lecture_data.get('description', '')

                # Handle file uploads if present
                if 'video' in lecture_data and lecture_data['video'] is not None:
                    lecture.video = lecture_data['video']

                if 'attachment' in lecture_data and lecture_data['attachment'] is not None:
                    lecture.attachment = lecture_data['attachment']

                lecture.save()

                # Create progress entries for students if needed
                self._create_lecture_progress(lecture)

            created_chapters.append(chapter)

        return created_chapters

    def _create_lecture_progress(self, lecture):
        # Get required models only when needed
        from lecture.models import LectureProgress
        from users.models import User

        chapter = lecture.chapter
        course = chapter.course
        semester = course.semester

        students = User.objects.filter(
            institution=course.institution,
            role="Student",
            semester=semester
        )

        progress_entries = [
            LectureProgress(enrollment=Enrollments.objects.get(
                user=student, course=course, is_completed=False), lecture=lecture, completed=False)
            for student in students
        ]

        if progress_entries:
            LectureProgress.objects.bulk_create(progress_entries)

    def to_representation(self, instance):
        return ChapterSerializer(instance, many=True, context=self.context).data
