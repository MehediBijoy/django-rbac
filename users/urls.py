from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from .auth.register import RegisterAPIView
from .auth.email_confirmation import EmailConfirmationAPIView

urlpatterns = [
    path('auth/login', TokenObtainPairView.as_view()),
    path('auth/signup', RegisterAPIView.as_view()),
    path('auth/email_confirmation', EmailConfirmationAPIView.as_view())
]
