from allauth.account.forms import ResetPasswordForm, ChangePasswordForm
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from .serializers import OTPSerializer, UserInformationSerializer, ChangePasswordSerializer, TempUserSerializer
from .models import TemporaryUser
from .utils import generate_otp
from rest_framework_simplejwt.authentication import JWTAuthentication
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, login

User = get_user_model()


def expiration_timestamp():
    expiration_duration = timezone.timedelta(minutes=3)
    return timezone.now() + expiration_duration


class SendOTPAPI(CreateAPIView):
    queryset = TemporaryUser.objects.all()
    serializer_class = TempUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user, _ = TemporaryUser.objects.update_or_create(
            email=email,
            defaults={
                'otp_code': generate_otp(),
                'otp_code_expiration': expiration_timestamp()
            }
        )

        print(f"OTP Code for {email}: {user.otp_code}")

        # Send OTP to the user
        send_mail(
            'Your OTP Code',
            f'Your OTP code is: {user.otp_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"detail": "OTP sent successfully."}, status=status.HTTP_201_CREATED)


class VerifyOTPAPI(CreateAPIView):
    serializer_class = OTPSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']

        user = TemporaryUser.objects.filter(email=email, otp_code=otp_code).first()
        if not user or not user.is_otp_valid():
            return Response({"detail": "Invalid or expired OTP code."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate or create user
        auth_user = User.objects.filter(email=email).first()
        if not auth_user:
            auth_user = User.objects.create_user(email=email, password=otp_code)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(auth_user)
        user.delete()  # Clean up temporary user

        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class UserInfoAPIView(RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserInformationSerializer

    def get_object(self):
        # The authenticated user can be accessed via self.request.user
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def get_response(self):
        response = super().get_response()
        user = self.user

        refresh = RefreshToken.for_user(user)
        response.data['access_token'] = str(refresh.access_token)
        response.data['refresh_token'] = str(refresh)

        return response


# Change Password View
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password1 = serializer.validated_data['new_password1']
            new_password2 = serializer.validated_data['new_password2']

            # Ensure the new passwords match
            if new_password1 != new_password2:
                return Response({"error": "Passwords do not match."}, status=400)

            # Use Allauth's password change functionality
            user = request.user
            form = ChangePasswordForm(user=user, data={'old_password': old_password, 'new_password1': new_password1,
                                                       'new_password2': new_password2})
            if form.is_valid():
                form.save()  # Save the new password
                return Response({"message": "Password changed successfully."}, status=200)
            else:
                return Response({"error": form.errors}, status=400)

        return Response(serializer.errors, status=400)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if email:
            try:
                user = get_user_model().objects.get(email=email)
                # Trigger password reset using Django All auth's built-in form
                form = ResetPasswordForm({'email': email})

                if form.is_valid():
                    form.save(request=request)  # This will send the password reset email
                    return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)
            except get_user_model().DoesNotExist:
                return Response({"message": "Email not found."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
