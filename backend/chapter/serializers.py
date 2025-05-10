from rest_framework import serializers
from chapter.models import Chapter
from courses.models import Course

class ChapterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chapter
        fields = (
            'id',
            'title',
            'course'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.user.role == "Institution":
            self.fields['course'].queryset = Course.objects.filter(institution=request.user)