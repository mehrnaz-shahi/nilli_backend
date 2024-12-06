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
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            # Try to get existing user
            user, created = TemporaryUser.objects.update_or_create(
                email=email,
                defaults={
                    'otp_code': generate_otp(),
                    'otp_code_expiration': expiration_timestamp()
                }
            )

            print(f"OTP Code for {email}: {user.otp_code}")

            # Send OTP to the user via email
            send_mail(
                'Your OTP code',
                f'Your OTP code is: {user.otp_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({"detail": "OTP sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPAPI(CreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            otp_code = serializer.validated_data['otp_code']
            email = request.data.get('email')
            user = TemporaryUser.objects.filter(email=email, otp_code=otp_code).first()
            if user:
                if user.is_otp_valid():
                    # OTP code is valid
                    # Check if user already exists or create new user
                    auth_user = self.authenticate_or_create_user(user)
                    if auth_user:
                        # Generate tokens
                        tokens = self.get_tokens(auth_user)
                        login(request, auth_user)
                        user.delete()  # delete temp user after login successfully
                        return Response(tokens, status=status.HTTP_200_OK)
                return Response({"detail": "Invalid or expired OTP code"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "You should give otp code first"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def authenticate_or_create_user(self, temp_user):
        # Check if user with phone number exists
        user = User.objects.filter(email=temp_user.email).first()
        if user:
            return user
        # Create new user based on temporary user info
        new_user = User.objects.create_user(
            email=temp_user.email,
            password=temp_user.otp_code
        )
        return new_user

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }

    # Optional: Override the get_serializer_class method to specify serializer class
    def get_serializer_class(self):
        return OTPSerializer


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
        # Get the original response from the parent class
        response = super().get_response()

        # Get the user from the response data
        user = self.user

        # Create JWT token for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Optionally save the token to the user's profile
        user.profile.jwt_token = access_token  # Assuming you have a `profile` model or similar
        user.profile.save()

        # Add JWT token to the response data
        response.data['access_token'] = access_token
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
