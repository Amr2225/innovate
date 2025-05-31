from rest_framework import serializers
from chapter.models import Chapter
from lecture.models import Lecture, LectureProgress
from users.models import User


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ('title', 'course')


class LectureSerializer(serializers.ModelSerializer):

    chapter_detials = ChapterSerializer(read_only=True)

    chapter = serializers.PrimaryKeyRelatedField(
        queryset=Chapter.objects.all(), write_only=True
    )

    class Meta:
        model = Lecture
        fields = ('id', 'title', 'video', 'attachment',
                  'chapter', 'chapter_detials')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.role == "Institution":
            self.fields['chapter'].queryset = Chapter.objects.filter(
                course__institution=request.user)

    def create(self, validated_data):
        lecture = Lecture.objects.create(**validated_data)

        chapter = lecture.chapter
        course = chapter.course
        semester = course.semester

        students = User.objects.filter(
            institution=course.institution,
            role="Student",
            semester=semester
        )

        progress_entries = [
            LectureProgress(user=student, lecture=lecture, completed=False)
            for student in students
        ]
        LectureProgress.objects.bulk_create(progress_entries)

        return lecture


class LectureProgressSerializer(serializers.ModelSerializer):
    lecture = serializers.PrimaryKeyRelatedField(
        queryset=Lecture.objects.all(), write_only=True)
    lecture_data = LectureSerializer(source='lecture', read_only=True)

    class Meta:
        model = LectureProgress
        fields = (
            'id',
            'lecture',
            'lecture_data',
            'completed'
        )

    def create(self, validated_data):
        request = self.context.get('request')
        lecture = validated_data.get('lecture')
        completed = validated_data.get('completed', False)

        progress, created = LectureProgress.objects.update_or_create(
            user=request.user,
            lecture=lecture,
            defaults={'completed': completed}
        )
        return progress


class LectureBulkCreateSerializer(serializers.Serializer):
    lectures = serializers.ListField(
        child=LectureSerializer(),
        min_length=1,
        required=True,
        error_messages={
            'required': 'A list of lectures is required for bulk creation.',
            'empty': 'At least one lecture must be provided for bulk creation.',
            'invalid': 'Invalid data format. Expected a list of lecture objects.'
        }
    )

    def validate_lectures(self, lectures_data):
        request = self.context.get('request')
        user = request.user

        for lecture_data in lectures_data:
            chapter = lecture_data.get('chapter')

            if user.role == "Teacher":
                if user not in chapter.course.instructors.all():
                    raise serializers.ValidationError(
                        f"You are not the instructor of the course for chapter: {chapter.title}")

            elif user.role == "Institution":
                if chapter.course.institution != user:
                    raise serializers.ValidationError(
                        f"You do not have permission to add a lecture to chapter: {chapter.title}")

        return lectures_data

    def create(self, validated_data):
        lectures_data = validated_data.get('lectures')
        lectures = []

        for lecture_data in lectures_data:
            lecture = Lecture.objects.create(**lecture_data)
            lectures.append(lecture)

            # Create progress entries for students
            chapter = lecture.chapter
            course = chapter.course
            semester = course.semester

            students = User.objects.filter(
                institution=course.institution,
                role="Student",
                semester=semester
            )

            progress_entries = [
                LectureProgress(user=student, lecture=lecture, completed=False)
                for student in students
            ]
            LectureProgress.objects.bulk_create(progress_entries)

        return lectures

    def to_representation(self, instance):
        return LectureSerializer(instance, many=True, context=self.context).data
