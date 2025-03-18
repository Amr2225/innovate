from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(method_name="get_birth_date")

    def get_birth_date(self, obj):
        print(obj)
        yearFirstNumbers = "20" if obj.national_id[0] == "3" else "19"
        year = f"{yearFirstNumbers}{ obj.national_id[1:3] }"
        month = obj.national_id[3:5]
        day = obj.national_id[5:7]
        return f"{month}/{day}/{year}"

    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_teacher", "full_name", "date")


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password',
                  'password_confirm', 'national_id', 'is_teacher', 'instituition')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        # Remove password_confirm field before creating the user
        validated_data.pop('password_confirm')

        return User.objects.create_user(**validated_data)


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for email verification."""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google authentication."""
    google_id = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
