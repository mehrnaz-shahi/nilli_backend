from rest_framework import serializers
from .models import User, TemporaryUser
from django.core.validators import EmailValidator


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[
            EmailValidator(
                message='Enter a valid email address.',
                code='invalid_email'
            )
        ]
    )
    otp_code = serializers.CharField(max_length=6)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']


class UserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class TempUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            EmailValidator(
                message='Enter a valid email address.',
                code='invalid_email'
            )
        ]
    )

    class Meta:
        model = TemporaryUser
        fields = ['email']


# Change Password Serializer
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)