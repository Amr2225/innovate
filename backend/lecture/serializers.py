# from rest_framework import serializers
# from chapter.models import Chapter
# from lecture.models import Lecture, LectureProgress
# from users.models import User
# from chapter.serializers import ChapterSerializer


# class LectureSerializer(serializers.ModelSerializer):
#     chapter_data = ChapterSerializer(source='chapter', read_only=True)

#     class Meta:
#         model = Lecture
#         fields = (
#             'id',
#             'title',
#             'description',
#             'video',
#             'attachment',
#             'chapter',
#             'chapter_data'
#         )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         request = self.context.get('request')
#         if request and request.user.role == "Institution":
#             self.fields['chapter'].queryset = Chapter.objects.filter(course__institution=request.user)

#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         rep.pop('chapter', None)
#         return rep

#     def create(self, validated_data):
#         lecture = Lecture.objects.create(**validated_data)

#         chapter = lecture.chapter
#         course = chapter.course
#         semester = course.semester

#         students = User.objects.filter(
#             institution=course.institution,
#             role="Student",
#             semester=semester
#         )

#         progress_entries = [
#             LectureProgress(user=student, lecture=lecture, completed=False)
#             for student in students
#         ]
#         LectureProgress.objects.bulk_create(progress_entries)

#         return lecture


# class LectureProgressSerializer(serializers.ModelSerializer):
#     lecture_data = LectureSerializer(source='lecture', read_only=True)

#     class Meta:
#         model = LectureProgress
#         fields = (
#             'id',
#             'lecture',
#             'lecture_data',
#             'completed'
#         )

#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         rep.pop('lecture', None)
#         return rep

#     def update(self, instance, validated_data):
#         instance.completed = validated_data.get('completed', instance.completed)
#         instance.save()
#         return instance

#     def create(self, validated_data):
#         request = self.context.get('request')
#         return LectureProgress.objects.create(user=request.user, **validated_data)


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
