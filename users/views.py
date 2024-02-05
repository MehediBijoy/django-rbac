from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer, ChangeEmailSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def email_change(self, request: Request, *args, **kwargs):
        serializer = ChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = self.get_object()
        user.email_change_request(serializer.validated_data['email'])

        return Response('success')
