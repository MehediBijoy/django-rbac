from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.request import Request
from users.models import JwtBlackList


class LogoutView(views.APIView):
    def delete(self, request: Request, *args, **kwargs):
        JwtBlackList.revoke_token(request.auth)
        return Response(status=status.HTTP_204_NO_CONTENT)
