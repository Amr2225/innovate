from rest_framework import serializers
from .models import McqQuestion
from decimal import Decimal

class McqQuestionSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    options = serializers.ListField(
        child=serializers.CharField(max_length=1000),
        required=False,
        write_only=True
    )
    question_grade = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal('0.00'))

    class Meta:
        model = McqQuestion
        fields = ('id', 'assessment', 'question', 'answer', 'answer_key', 'created_by', 'options', 'question_grade')
        read_only_fields = ('answer',)
        extra_kwargs = {
            'answer_key': {'write_only': True}  # Hide answer key from students
        }

    def validate(self, data):
        if 'options' in data:
            if len(data['options']) < 2:
                raise serializers.ValidationError("At least 2 options are required")
            data['answer'] = data['options']
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add options from answer field
        data['options'] = instance.answer
        
        # Remove answer key for students
        request = self.context.get('request')
        if request and request.user.role == 'Student':
            data.pop('answer_key', None)
            
        return data
