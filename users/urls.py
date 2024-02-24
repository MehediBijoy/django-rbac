from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.users import UserViewSet

router = DefaultRouter(trailing_slash=False)
router.register('', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
