from rest_framework import serializers
from chapter.models import Chapter
from lecture.models import Lecture, LectureProgress
from users.models import User

class LectureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lecture
        fields = (
            'id',
            'title',
            'description',
            'video',
            'attachment',
            'chapter',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.user.role == "Institution":
            self.fields['chapter'].queryset = Chapter.objects.filter(course__institution=request.user)
    
    def create(self, validated_data):
        lecture = Lecture.objects.create(**validated_data)

        chapter = lecture.chapter
        course = chapter.course
        semester = course.semester

        students = User.objects.filter(institution=course.institution, role="Student", semester=semester)

        progress_entries = [
            LectureProgress(user=student, lecture=lecture, completed=False)
            for student in students
        ]
        LectureProgress.objects.bulk_create(progress_entries)

        return lecture



class LectureProgressSerializer(serializers.ModelSerializer):

    class Meta:
        model = LectureProgress
        fields = (
            'id',
            'lecture',
            'completed'
        )
    
    def update(self, instance, validated_data):
        instance.completed = validated_data.get('completed', instance.completed)
        instance.save()
        return instance

    def create(self, validated_data):
        request = self.context.get('request')
        lectureProgress = LectureProgress.objects.create(user=request.user, **validated_data)
        return lectureProgress