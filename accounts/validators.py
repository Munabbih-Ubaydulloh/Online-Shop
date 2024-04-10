from rest_framework.exceptions import ValidationError
import re
from .models import User

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
            raise ValidationError({"success":False, "message":"Bu nomer ro'yhatdan o'tkazilgan !!!"})
    return True


