from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User
from users.serializers import UserSerializer


class EmailConfirmationAPIView(APIView):
    permission_classes = []

    def get(self, request: Request):
        token = request.query_params.get('confirmation_token')
        if not token:
            raise ValidationError('Token is not present')

        try:
            user = User.objects.get(confirmation_token=token)
        except:
            raise ValidationError('Invalid email confirmation token')
        else:
            user.confirm()
            """
            If we want to add extra claim here 
            we can simply add ref_token['role'] = user.role
            """
            ref_token = AccessToken.for_user(user)

        return Response(data={
            'user': UserSerializer(instance=user).data,
            'token': str(ref_token)
        })


class ResendEmailConfirmation(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        user: User = request.user
        user.resend_email_confirmation()

        return Response(data='success')
