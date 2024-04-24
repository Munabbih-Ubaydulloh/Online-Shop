from typing import Any, Dict
from rest_framework import serializers
from .models import Address, Profile, User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import authenticate
from rest_framework import exceptions
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from .validators import validate_password_strength, validate_phone_number

def authenticate_user(request=None, phone=None, password=None, **kwargs):
    user = authenticate(phone=phone, password=password)
    print(user)
    if user is None:

        raise AuthenticationFailed("Kiritilgan ma'lumotlarga ega foydalanuvchi topilmadi!")
    return user


class SignUpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id", 'phone', 'password']
        extra_kwargs = {
            "phone" : {"validators":[]}
        }

    def validate(self, attrs):
        validate_phone_number(attrs['phone'])
        validate_password_strength(attrs['password'])
        return attrs   
    
    def create(self, validated_data):
        
        password = validated_data['password']
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'phone', 'is_seller', 'is_active']


class LoginSerializer(TokenObtainSerializer):

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user=user)
    
    default_error_messages = {
        "no_account_found"  : "Bu ma'lumotga ega aktiv foydalanuvchi topilmadi"
    }


    def validate_user(self, attrs):

        # authencication_credentials = {
        #     "phone" : attrs['phone'],
        #     "password" : attrs("password")
        # }
        phone, password = attrs['phone'], attrs['password']
        self.user = authenticate_user(self.context['request'], phone=phone, password=password)
        
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            self.fail("no_account_found")

        return {}
    
    def validate(self, attrs):

        data = self.validate_user(attrs=attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['id'] = str(self.user.id)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
    

class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()


    default_error_messages = {
        "bad_token" : 'Mavjud bo\'lmagan token kiritildi'
        }

    def validate(self, attrs):
        
        self.token = attrs['refresh']
 
        return attrs
    
    def save(self, **kwargs):
        
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")


class ChangePhoneSerializer(serializers.Serializer):

    phone = serializers.CharField(max_length=13)
    new_phone = serializers.CharField(max_length=13)



class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User

    def validate(self, attrs):
        
        validate_password_strength(attrs['new_password'])

        return attrs


class CreateProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = Profile 
        fields = ['first_name', 'last_name', 'email']


class AddressSerializer(serializers.ModelSerializer):

    class Meta:

        model = Address 
        fields = ['id', 'title', 'country', 'province', 'district', 'street', 'zip_code']

