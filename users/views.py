from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['get'])
@permission_classes([IsAuthenticated])
def get_name(request: Request):
    return Response('ok')
