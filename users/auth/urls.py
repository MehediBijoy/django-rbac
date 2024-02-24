from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .login import LoginSerializer
from .register import RegisterAPIView
from .profile import ProfileAPIView
from .email_confirmation import EmailConfirmationAPIView


urlpatterns = [
    path('login', TokenObtainPairView.as_view(serializer_class=LoginSerializer)),
    path('signup', RegisterAPIView.as_view()),
    path('profile', ProfileAPIView.as_view()),
    path('email_confirmation', EmailConfirmationAPIView.as_view())
]
