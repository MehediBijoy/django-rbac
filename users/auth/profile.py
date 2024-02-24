from rest_framework import status, views
from rest_framework.request import Request
from rest_framework.response import Response

from users.serializers.users import UserSerializer


class ProfileAPIView(views.APIView):
    def get(self, request: Request):
        return Response(
            data=UserSerializer(instance=request.user).data,
            status=status.HTTP_200_OK
        )
