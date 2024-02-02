from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from .auth.login import LoginSerializer
from .auth.register import RegisterAPIView

urlpatterns = [
    path('auth/login', TokenObtainPairView.as_view(serializer_class=LoginSerializer)),
    path('auth/signup', RegisterAPIView.as_view()),
]
