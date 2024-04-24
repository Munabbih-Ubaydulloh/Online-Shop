from django.shortcuts import render, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import (
    GenericAPIView, CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
)
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status, permissions
from .validators import validate_phone_number , find_None
from rest_framework_simplejwt.views import TokenViewBase
from .models import ( User, Profile, Address, Confirmation, 
        UploadFile, ProfilePictures )
from django.utils import timezone
import random
from .utils import send_ms_to_channel
from rest_framework.decorators import api_view, permission_classes

class SignUpView(APIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer

    def post(self, request:Request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"success":True, "message" : "Ro'yhatdan o'tish muvofaqqiyatli kodni tasdiqlang!"})

@api_view(http_method_names=['POST'])
@permission_classes([])
def create_user(request):

    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data=serializer.data, status=status.HTTP_201_CREATED)

class RetrieveOrUserListAPIView(RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    
    def get_user_data(self, pk=None):

        if pk:
            user_qs = User.objects.filter(pk=pk)
            if user_qs.exists():
                user = user_qs.last()
                data = {
                    "id" : user.id,
                    "phone" : user.phone,
                    "is_seller" : user.is_seller,
                    "is_active" : user.is_active,
                    "activated_data" : user.activated_date
                }

                profile = Profile.objects.filter(user_id=user.id)
                if profile.exists():

                    data['profile'] = (profile.last()).id

                return Response(data=data, status=status.HTTP_200_OK)
            return Response(data={"success":False, "message" : "Bunday foydalanuvchi mavjud emas!"})
        else:

            users = User.objects.all()
            user_list = []

            for user in users:

                data = {
                    "id" : user.id,
                    "phone" : user.phone,
                    "is_seller" : user.is_seller,
                    "is_active" : user.is_active
                }
                profile = get_object_or_404(Profile, user__id=user.id)

                data['profile'] = profile.id

                user_list.append(data)
            
            return Response(data=user_list, status=status.HTTP_200_OK)
    

    def get(self, request:Request, *args, **kwargs):

        return self.get_user_data(kwargs.get('pk', None))

    def delete(self, request:Request, *args, **kwargs):
        self.destroy(self, *args, **kwargs)

        return Response(data={"success":True, 'message':"Foydalanuvchi muvofaqqiyatli o'chirildi"}, status=status.HTTP_204_NO_CONTENT)

class LoginView(TokenViewBase):

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

class LogoutView(APIView):
    
    serializer_class = LogoutSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request:Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = {
            "success" : True,
            "message" : "Tizimdan chiqish muvofaqqiyatli"
        }

        return Response(data=response, status=status.HTTP_205_RESET_CONTENT)
    

class VerifyView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request:Request, *args, **kwargs):
        
        phone = request.data.get("phone", None)
        new_phone = request.data.get("new_phone", None)
        type = request.data.get("type", None)
        code = request.data.get("code", None)
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(data={"success":False, "message":"Kiritilgan telefon raqamli foydalanuvchi mavjud emas!"}, status=status.HTTP_404_NOT_FOUND)
        print(new_phone, phone, type, code )

        if None in (phone, new_phone, type, code) and type == "change_phone":
            
            return find_None([phone, new_phone, type, code])
        print(user)
        qs = Confirmation.objects.filter(user=user, expiration_time__gte=timezone.now(), is_confirmed=False) # is_confirmed=False))
        print(qs.last())
        if qs.exists():
            obj = qs.last()
            print(obj.code, code)
            if obj.code != code:
                response = {
                    "success" : False,
                    "message" : "Noto'g'ri kod kiritildi"
                }
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
            obj.activate()
        
            if type == 'change_phone':

                user.phone = new_phone
                user.save()

                message = 'Kod tasdiqlandi. Telefonni yangilash muvofaqqiyatli!'

            elif type == "password_reset":
                message = 'Kod tasdiqlandi. Parolni tiklashga ruhsat berildi!'

            else:
                message = "Kod tasdiqlandi. Ro'yhatdan o'tish muvofaqqiyatli!"

            return Response(data={"success":True, "message":message})
        
        else:

            if Confirmation.objects.filter(user=user):
                return Response(data={"success":False, "message":"Kodning aktivlik muddati o'tgan, davom etish uchun kodni qayta yuboring"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                response = {"success" : False, "message" : "Telefon raqami noto'g'ri kiritildi"}

                return Response(data=response, status=status.HTTP_404_NOT_FOUND)
        

class ChangePhoneView(APIView):

    permission_classes = [permissions.AllowAny]
    def patch(self, request:Request):
        
        serializer = ChangePhoneSerializer(data=request.data)

        if serializer.is_valid():

            new_phone = serializer.validated_data['new_phone']

            validate_phone_number(new_phone)

            user:User = request.user
            print(user)
            user.edit_phone()

            return Response(data={"success":True, "message" : "Telefon raqamini yangilash so'rovi yuborildi kodni tasdiqlang!"}, status=status.HTTP_200_OK)
        else:
            Response(data={"success":False, "message" : "To'g'ri telefon raqamini kiriting!"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    model = User

    def update(self, request:Request, *args, **kwargs):
        self.object = self.request.user
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            if not self.object.check_password(serializer.validated_data.get("old_password")):
                return Response(data={"success" : False, "message" : "Parol noto'g'ri kiritildi!"}, status=status.HTTP_400_BAD_REQUEST)
             
            self.object.set_password(serializer.validated_data['new_password'])
            self.object.save()

            response = {
                "success" : True,
                "message" : "Parol yangilash muvofaqqiyatli bajarildi!"
            }           
            return Response(data=response, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetAPIView(GenericAPIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request:Request, *args, **kwargs):

        phone = request.data.get("phone", None)
        user = User.objects.filter(phone=phone)

        if user.exists():
            code = "".join(str(random.randint(0,9)) for _ in range(6))
            Confirmation.objects.create(
                user = user.last() ,
                code = code ,
                type = "password_reset" , 
                expiration_time = timezone.now() + timezone.timedelta(minutes=3)
            )
            send_ms_to_channel(code=code)
            data = {
                "success" : True,
                "message" : "Parol tiklash arizasi qabul qilindi. Kodni tasdiqlang!"
            }
            return Response(data=data, status=status.HTTP_200_OK)
        
        return Response(data={"success" : False, "message" : "Bunday telefon raqamli foydalanuvchi mavjud emas!"})


class PasswordResetConfirmAPIView(GenericAPIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request:Request, *args, **kwargs):

        phone = request.data.get("phone")
        password = request.data.get("password")
        password2 = request.data.get("password2")

        if not password == password2 :

            return Response(data={"success" : False, "message" : "Kiritilgan parollar bir biriga mos emas!"})

        user = get_object_or_404(User, phone=phone)

        user.set_password(password)
        user.save()

        return Response(data={"success" : True , "message" : "Parol muvofaqqiyatli yangilandi!"})
    

class ResendCodeAPIView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request:Request, *args, **kwargs):

        phone = request.data.get("phone")
        type = request.data.get("type")

        if type == None or phone == None :

            return Response(data={"success" : False, "message": "Ma'lumot to'liq kiritilmadi! Kerakli ma'lumotlar ['phone', 'type']"})

        user = get_object_or_404(User, phone=phone)
        expirations = Confirmation.objects.filter(user=user)
        expirations.delete()

        if type in ['register', 'password_reset', "change_phone"]:
            code = "".join(str(random.randint(0,9)) for _ in range(6))
            user = Confirmation.objects.create(user=user, expiration_time=timezone.now() + timezone.timedelta(minutes=3), code=code)
            send_ms_to_channel(code=code)

        else:
            return Response(data={"success":False, "message" : "Bunday tasdiqlash turi mavjud emas"})

        return Response(data={"success":True, "message":"Kod qayta yuborildi, tasdiqlang!"})


class CheckUserPassword(APIView):

    permission_classes = [permissions.AllowAny]
    def post(self, request:Request):

        phone = request.data.get("phone")
        password = request.data.get("password")

        user = User.objects.filter(phone=phone).first()

        ps_check = user.check_password(password)

        return Response(data={"is user's password" : ps_check}, status=status.HTTP_200_OK)


################################### User Profile Section #################################################


class ListCreateProfileAPIView(ListCreateAPIView):

    serializer_class = CreateProfileSerializer
    permission_classes = permissions.AllowAny,
    queryset = Profile.objects.all()



    def post(self, request:Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        image = request.data.get('image', None)
        email = request.data.get("email", None)
        user = request.user
        if Profile.objects.filter(user=user).exists():

            return Response(data={"success" : False, "message" : "Bu foydalanuvchi profili mavjud"})
        
        profile = Profile.objects.create(
            user = user,
            first_name = first_name,
            last_name = last_name,
            email = email

        )

        if image is None:
            return Response(data={"success" : False, "message" : "Rasm yuklashda xatolik sodir bo'ldi!"})
        else:
            profile.set_image(image=image)
            profile.save()
        
        response = {
            "success" : True,
            "message" : "Profil muvaffaqqiyatli yaratildi!"
        }
        return Response(data=response, status=status.HTTP_201_CREATED)
    

class ProfileAPIView(RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.AllowAny]
    queryset = Profile.objects.all()
    serializer_class = CreateProfileSerializer

    def get(self, request, *args, **kwargs):
        profile_ = Profile.objects.filter(id=kwargs['pk'])
        profile = profile_.last()
        image = ProfilePictures.objects.filter(profile=profile).last()
        # print(image.image.file.url)
        if profile_.exists():

            data = {
                'id': profile.id,
                'first_name': profile.first_name,
                "last_name": profile.last_name,
                'email': profile.email,  
                "image" : image.image.file.url,  
                "user": profile.user.phone,
                "user_id": profile.user.id,
            }
            
            address_ = Address.objects.filter(profile=profile)

            if address_.exists():
                address = address_.last()
                data['address'] = address.id
            
            return Response(data={"success": True, "data": data})
        else:
            return Response(data={"success": False, "message": "Bunday Profil mavjud emas!"})

        
    
    def patch(self, request:Request, *args, **kwargs):
        
        if 'image' in request.FILES:
            profile_ = Profile.objects.filter(user=request.user)
            file = UploadFile.objects.create(file=request.FILES.get("image"))
            if profile_.exists():
                profile = profile_.first()
                try:
                    image = ProfilePictures.objects.filter(profile=profile).last()
                    image.delete()
                except Exception as e:
                    print(e.args) 
                profile.set_image(image=file)
            else:
                return Response(data={"success" : False, "message" : "Bunday Profil mavjud emas!"})
        self.partial_update(request, *args, **kwargs)

        return Response(data={"success" : True, "message" : "Profil ma'lumotlari yangilandi!"})  
            

    def delete(self, request:Request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)

        return Response(data={"success":True, "message" : "Profil muvaffaqiyatli o'chirildi!"}, status=status.HTTP_204_NO_CONTENT)


#################################### User Address Section ################################################# 


class AddressListCreateView(ListCreateAPIView):

    permission_classes = permissions.IsAuthenticated,
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.all()
    

    def perform_create(self, serializer):
        
        user = self.request.user
        profile = get_object_or_404(Profile, user__id=user.id)
        serializer.save(profile=profile)


    def post(self, request:Request, *args, **kwargs):

        profile = Profile.objects.filter(user=self.request.user)
        zip_code = request.data.get("zip_code", None)
        if Address.objects.filter(profile=profile.last(), zip_code=zip_code).exists():
            return Response(data={"success" : False, "message" : "Bu foydalanuvchining manzili mavjud"})

        self.create(request, *args, **kwargs)
        return Response(data={"success" : True, "message" : "Manzil ma'lumotlari saqlandi"})



class AddressAPIView(RetrieveUpdateDestroyAPIView):

    serializer_class = AddressSerializer
    permission_classes = permissions.IsAuthenticated,

    def get_queryset(self):
        user = self.request.user
        profile = Profile.objects.filter(user=user).last()
        
        return Address.objects.filter(profile=profile)
    
    def patch(self, request:Request, *args, **kwargs):

        self.partial_update(request, *args, **kwargs)
        return Response(data={"success" : True, "message" : "Manzil ma'lumotlari yangilandi"})
        
    def delete(self, request:Request, *args, **kwargs):

        self.destroy(request, *args, **kwargs)
        return Response(data={"success" : True, "message" : "Manzil muvaffaqiyatli o'chirildi!"} , status=status.HTTP_204_NO_CONTENT)




        