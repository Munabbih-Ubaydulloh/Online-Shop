from rest_framework.exceptions import ValidationError
import re
from .models import User
from rest_framework import serializers
from rest_framework.response import Response

def validate_phone_number(phone):

    phone_regexp = r"^[\+]?[(]?[9]{2}?[8]{1}[)]?[-\s\.]?[0-9]{2}[-\s\.]?[0-9]{7}$"

    is_match = re.fullmatch(phone_regexp, phone)
    
    if not is_match:
        data = {
            "success" : False,
            "message" : "Telefon raqami to'g'ri kiritilmadi!"
        }
        raise ValidationError(data)
    
    if User.objects.filter(phone=phone).exists():
            raise ValidationError({"message":"Bu nomer ro'yhatdan o'tkazilgan !!!"})
    return True


def validate_password_strength(password):
    katta = False
    kichik = False
    belgi = False
    raqam = False
   # Lonewalker114
    belgilar = (".", "_", "*", "-", "$", "#")
    for char in password:   
        if 64 < ord(char) < 92:
            katta = True
        elif 96 < ord(char) < 123:
            kichik = True
        elif char in belgilar:
            belgi = True
        elif char.isnumeric():
            raqam = True    
    if len(password) < 8:
            raise serializers.ValidationError({"success":False, "message" : "Parol 8 belgidan kam bo'lmasligi kerak"})
    if (katta+kichik+belgi+raqam) < 2:
        print(katta,kichik,belgi, raqam)
        raise serializers.ValidationError({"success":False, "message" : f"Parol xavfsizlik talabiga javob bermaydi! Katta va kichik harflar yoki {belgilar} belgilaridan foydalaning"})
    return True


def find_None(data:list):
    Nones = []
    index_data = {1 : "phone", 2 : "change_phone", 3 : "type", 4 : "code"}
    for index , none in enumerate(data):
       if none is None:
           Nones.append(index_data[index+1]) 
    if len(Nones):
        return Response(data={"success":False, 'message' : "Barcha ma'lumotlar keltirilmadi! Kerakli ma'lumotlar : {}".format(Nones)})





