from rest_framework import serializers
from .models import McqQuestion

class McqQuestionSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    options = serializers.ListField(
        child=serializers.CharField(max_length=1000),
        min_length=4,
        max_length=4,
        required=False,
        write_only=True
    )

    class Meta:
        model = McqQuestion
        fields = ('id', 'assessment', 'question', 'answer', 'answer_key', 'created_by', 'options')
        read_only_fields = ('answer',)
        extra_kwargs = {
            'answer_key': {'required': False}
        }

    def validate(self, data):
        """
        Validate the MCQ data for manual creation
        """
        if self.context['request'].method in ['POST', 'PUT']:
            options = data.get('options')
            answer_key = data.get('answer_key')

            if options is not None:
                if not answer_key:
                    raise serializers.ValidationError({"answer_key": "Answer key is required when providing options"})
                if answer_key not in options:
                    raise serializers.ValidationError({"answer_key": "Answer key must be one of the provided options"})
                # Store options in answer field
                data['answer'] = options

        return data

    def to_representation(self, instance):
        """
        Customize the output representation
        """
        data = super().to_representation(instance)
        # Add options from answer field
        data['options'] = instance.answer
        return data
