from django.contrib import auth
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

@api_view(['POST'])
def change_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        old_password = data['password']
        new_password = data['new_password']
        verify = auth.authenticate(request,username=username,password=old_password)
        if verify:
            user = User.objects.get(username=username)
            print(user)
            if user:
                user.set_password(new_password)
                user.save()
                return_string = '{"result":1}'
            else:
                return_string = '{"result":"error"}'
        else:
            # verify failed return -2
            return_string = '{"result":-1}'
        ret= json.loads(return_string)
        print(ret)
        return Response(ret)
    def perform_authentication(self, request):
        pass

