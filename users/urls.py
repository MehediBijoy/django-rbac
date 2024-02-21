from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from .views.user import UserViewSet
from .auth.profile import Profile
from .auth.register import RegisterAPIView
from .auth.email_confirmation import EmailConfirmationAPIView, ResendEmailConfirmation

router = DefaultRouter(trailing_slash=False)
router.register('', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login', TokenObtainPairView.as_view()),
    path('auth/signup', RegisterAPIView.as_view()),
    path('auth/email_confirmation', EmailConfirmationAPIView.as_view()),
    path('auth/resend_email_confirmation', ResendEmailConfirmation.as_view()),
    path('auth/profile', Profile.as_view()),
]
