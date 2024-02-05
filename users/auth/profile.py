from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.serializers import UserSerializer


class Profile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        return Response(data=UserSerializer(instance=request.user).data)
