from rest_framework import serializers
from .models import McqQuestion

class McqQuestionSerializer(serializers.ModelSerializer):
    choices_count = serializers.SerializerMethodField()

    class Meta:
        model = McqQuestion
        fields = [
            'id',
            'assessment',
            'question',
            'points',
            'answer',
            'answer_key',
            'choices_count',
            'created_at',
            'updated_at',
            'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
        extra_kwargs = {
            'answer_key': {'write_only': True}  # Hide correct answer in GET responses
        }

    def get_choices_count(self, obj):
        return obj.get_choices_count()

    def validate_answer(self, value):
        """
        Validate the answer format
        Expected format: [{"key": "A", "text": "Choice text"}, ...]
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Choices must be a list")
        
        if not value:
            raise serializers.ValidationError("Must provide at least one choice")
        
        # Validate each choice
        valid_keys = []
        for i, choice in enumerate(value):
            if not isinstance(choice, dict):
                raise serializers.ValidationError(f"Choice {i} must be a dictionary")
            
            if 'key' not in choice or 'text' not in choice:
                raise serializers.ValidationError(f"Choice {i} must have 'key' and 'text' fields")
            
            # Validate key format
            key = choice['key'].upper()
            if not key.isalpha() or len(key) != 1:
                raise serializers.ValidationError(f"Choice key '{key}' must be a single letter")
            
            valid_keys.append(key)
        
        # Check for duplicate keys
        if len(valid_keys) != len(set(valid_keys)):
            raise serializers.ValidationError("Choice keys must be unique")
        
        return value

    def validate(self, data):
        """
        Validate that answer_key corresponds to one of the choices
        """
        answer = data.get('answer', [])
        answer_key = data.get('answer_key', '').upper()
        
        valid_keys = [choice['key'].upper() for choice in answer]
        if answer_key not in valid_keys:
            raise serializers.ValidationError({
                "answer_key": "Must be one of the choice keys"
            })
        
        return data
