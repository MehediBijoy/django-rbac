from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView

from .profile import ProfileAPIView
from .register import RegisterAPIView
from .login import LoginSerializer, AdminLoginSerializer
from .email_confirmation import EmailConfirmationAPIView, AdminEmailConfirmationAPIView

admin_urlpatterns = [
    path('login', TokenObtainPairView.as_view(serializer_class=AdminLoginSerializer)),
    path('email_confirmation', AdminEmailConfirmationAPIView.as_view())
]

urlpatterns = [
    path('login', TokenObtainPairView.as_view(serializer_class=LoginSerializer)),
    path('signup', RegisterAPIView.as_view()),
    path('profile', ProfileAPIView.as_view()),
    path('email_confirmation', EmailConfirmationAPIView.as_view()),
    path('admin/', include(admin_urlpatterns)),
]
