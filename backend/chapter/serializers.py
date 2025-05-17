from rest_framework import serializers
from chapter.models import Chapter
from lecture.serializers import LectureSerializer
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
