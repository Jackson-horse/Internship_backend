from django.shortcuts import render
from rest_framework_simplejwt.views import TokenViewBase,TokenObtainPairView as BaseTokenObtainPairView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .serializers import TokenObtainPairSerializer

class TokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

class TokenRefreshView(TokenViewBase):
    serializer_class = TokenRefreshSerializer

