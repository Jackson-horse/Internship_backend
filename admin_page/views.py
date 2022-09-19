from rest_framework.decorators import permission_classes,api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_database(request):
    return Response("ok")