from rest_framework import serializers
from chapter.models import Chapter
from lecture.models import Lecture, LectureProgress

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



class LectureProgressSerializer(serializers.ModelSerializer):

    class Meta:
        model = LectureProgress
        fields = (
            'id',
            'user',
            'lecture',
            'completed'
        )
    
    def update(self, instance, validated_data):
        instance.completed = validated_data.get('completed', instance.completed)
        instance.save()
        return instance

    def create(self, validated_data):
        return LectureProgress.objects.create(**validated_data)