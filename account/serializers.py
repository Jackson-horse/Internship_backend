from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as BaseTokenObtainPairSerializer

class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):

    def validate(self,attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        if self.user.is_staff:
            data['is_staff']=True
        else:
            data['is_staff']=False
        return data