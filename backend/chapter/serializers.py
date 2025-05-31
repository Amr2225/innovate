from rest_framework import serializers
from chapter.models import Chapter
from courses.models import Course
from courses.serializers import CourseSerializer

class ChapterSerializer(serializers.ModelSerializer):
    course_data = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = (
            'id',
            'title',
            'course',
            'course_data',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.role == "Institution":
            self.fields['course'].queryset = Course.objects.filter(institution=request.user)
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop('course', None)
        return rep

    def get_course_data(self, obj):
        serializer_context = {'request': self.context.get('request')} if self.context.get('request') else {}
        return CourseSerializer(obj.course, context=serializer_context).data
