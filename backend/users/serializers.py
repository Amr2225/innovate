# from rest_framework import serializers
# from users.models import User


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     confirm_password = serializers.CharField(write_only=True, min_length=8)

#     class Meta:
#         model = User
#         fields = (
#             'email',
#             'first_name',
#             'last_name',
#             'avatar',
#             'is_teacher',
#             'national_id',
#             'instituition',
#             'password',
#             'confirm_password',
#         )

#     def validate(self, data):
#         if data['password'] != data['confirm_password']:
#             raise serializers.ValidationError("Passwords do not match.")
#         return data

#     def create(self, validated_data):
#         user = User(
#             email=validated_data['email'],
#             first_name=validated_data['first_name'],
#             last_name=validated_data['last_name'],
#             avatar=validated_data.get('avatar', None),
#             is_teacher=validated_data.get('is_teacher', False),
#             national_id=validated_data['national_id'],
#             instituition=validated_data.get('instituition', None),
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user
