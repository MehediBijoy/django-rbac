from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import views, exceptions, permissions

from users.models import User
from users.helper import UserAuthResponse
from users.services import NotificationService
from users.permissions import IsAdmin, IsUser


class EmailConfirmationAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsUser]

    def get(self, request: Request):
        request.user.resend_email_confirmation()
        return Response(data='success')

    def post(self, request: Request):
        token = request.data.get('confirmation_token')
        if not token:
            raise exceptions.ValidationError('Token is not present')

        try:
            user = User.objects.get(confirmation_token=token)
            user.confirm()
        except User.DoesNotExist:
            raise exceptions.ValidationError('Invalid email confirmation token')

        NotificationService.notify(
            user=user,
            triggered_by='email_confirmation',
            payload={'email': user.email, 'confirmed_at': user.confirmed_at}
        )

        return Response(UserAuthResponse(user).data)


class AdminEmailConfirmationAPIView(EmailConfirmationAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
