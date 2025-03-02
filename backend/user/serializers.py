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
