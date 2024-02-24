from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from users.models import User
from users.helper import UserAuthResponse
from users.services import NotificationService


class EmailConfirmationAPIView(APIView):
    permission_classes = []

    def get(self, request: Request):
        token = request.query_params.get('confirmation_token')
        if not token:
            raise ValidationError('Token is not present')

        try:
            user = User.objects.get(confirmation_token=token)
            user.confirm()
        except User.DoesNotExist:
            raise ValidationError('Invalid email confirmation token')

        NotificationService.notify(
            user=user,
            triggered_by='email_confirmation',
            payload={'email': user.email, 'confirmed_at': user.confirmed_at}
        )

        return Response(UserAuthResponse(user).data)


class ResendEmailConfirmation(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        request.user.resend_email_confirmation()
        return Response(data='success')
