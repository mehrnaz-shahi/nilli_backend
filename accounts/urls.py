from dj_rest_auth.views import LogoutView
from django.urls import path, include
from .views import SendOTPAPI, VerifyOTPAPI, UserInfoAPIView, GoogleLogin

urlpatterns = [
    path('sendOTP/', SendOTPAPI.as_view(), name='send_otp_code'),
    path('verifyOTP/', VerifyOTPAPI.as_view(), name='verify_otp_code'),
    path('whoami/', UserInfoAPIView.as_view(), name='whoami'),
    path('', include('allauth.urls')),
    path('authentication/', include('dj_rest_auth.urls')),  # Login/logout endpoints
    path('registration/', include('dj_rest_auth.registration.urls')),  # Registration endpoints
    path('logout', LogoutView.as_view()),
]
