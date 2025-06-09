from rest_framework import serializers
from decimal import Decimal
import logging
from .models import McqQuestion


logger = logging.getLogger(__name__)

class McqQuestionSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    options = serializers.ListField(
        child=serializers.CharField(max_length=1000),
        required=True
    )
    question_grade = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal('0.00'))
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    section_number = serializers.IntegerField(default=1, min_value=1)

    class Meta:
        model = McqQuestion
        fields = (
            'id', 'assessment', 'question', 
            'options', 'answer_key', 'created_by', 'question_grade',
            'created_at', 'updated_at', 'section_number'
        )
        read_only_fields = ('created_at', 'updated_at', 'created_by')
        extra_kwargs = {
            'answer_key': {'write_only': True}  # Hide answer key from students
        }

    def validate(self, data):
        try:
            logger.info("Starting validation of MCQ question data")
            logger.debug(f"Validation data: {data}")
            
            # Validate options
            if 'options' in data:
                if len(data['options']) < 2:
                    raise serializers.ValidationError("At least 2 options are required")
                if len(data['options']) > 6:
                    raise serializers.ValidationError("Maximum 6 options allowed")
                
                # Validate that answer_key matches one of the options
                if 'answer_key' in data and data['answer_key'] not in data['options']:
                    raise serializers.ValidationError("Answer key must match one of the options")

            # Validate question
            if 'question' in data and not data['question'].strip():
                raise serializers.ValidationError("Question cannot be empty")

            # Validate assessment
            if 'assessment' not in data:
                raise serializers.ValidationError("Assessment is required")

            logger.info("Validation completed successfully")
            return data
        except Exception as e:
            logger.error(f"Validation error in McqQuestionSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        try:
            logger.info("Starting creation of MCQ question")
            logger.debug(f"Validated data: {validated_data}")
            
            # Get the request user from context
            request_user = self.context.get('request').user
            logger.debug(f"Request user: {request_user}")
            
            # Create the instance
            try:
                instance = self.Meta.model.objects.create(
                    question=validated_data['question'],
                    options=validated_data['options'],
                    answer_key=validated_data['answer_key'],
                    assessment=validated_data['assessment'],
                    question_grade=validated_data.get('question_grade', Decimal('0.00')),
                    section_number=validated_data.get('section_number', 1),
                    created_by=request_user
                )
                logger.info(f"Successfully created MCQ question with ID: {instance.id}")
                return instance
            except Exception as create_error:
                logger.error(f"Error during model creation: {str(create_error)}")
                logger.error(f"Error type: {type(create_error)}")
                raise
            
        except Exception as e:
            logger.error(f"Error in create method: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            raise serializers.ValidationError(f"Error creating question: {str(e)}")

    def to_representation(self, instance):
        try:
            data = super().to_representation(instance)
            
            # Remove answer key for students
            request = self.context.get('request')
            if request and request.user.role == 'Student':
                data.pop('answer_key', None)
                
            return data
        except Exception as e:
            logger.error(f"Error in to_representation: {str(e)}")
            raise serializers.ValidationError(f"Error processing question data: {str(e)}")
