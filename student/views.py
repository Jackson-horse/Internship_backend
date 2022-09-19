from rest_framework.decorators import permission_classes,api_view
from .permissions import IsAuthenticatedButNotAdmin
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticatedButNotAdmin])
def course_recommendation(request):
    # print(request.META.get('Authorization'))
    return Response("ok")

