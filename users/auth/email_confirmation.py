from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from users.models import User


class EmailConfirmationAPIView(APIView):
    def get(self, request: Request):
        token = request.query_params.get('confirmation_token')
        if not token:
            raise ValidationError('Token is not present')

        try:
            user = User.objects.get(confirmation_token=token)
        except:
            raise ValidationError('Invalid confirmation token')
        else:
            # implement later
            pass

        return Response('success')
