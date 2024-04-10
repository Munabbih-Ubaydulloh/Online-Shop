from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import (
    GenericAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status, permissions
from .validators import validate_phone_number

class SignUpView(APIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer


    def post(self, request:Request, *args, **kwargs):

        phone = request.data.get("phone", None)
        validate_phone_number(phone=phone)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(data={"success":True, "message":"You have successfully been registered!!!"})


class AllUsersView(APIView):

    serializer_class = UserSerializer 
    permission_classes = [permissions.AllowAny]

    def get(self, request:Request, *args, **kwargs):
        
        users = User.objects.all()
        serializer = self.serializer_class(instance=users, many=True)

        return Response(data=serializer.data)
    