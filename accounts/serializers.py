from rest_framework import serializers
from .models import User



class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", 'phone', 'password']

    
    def validate(self, attrs):
        katta = False
        kichik = False
        belgi = False
        raqam = False

        password = attrs['password']     # Lonewalker114
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
            
        return attrs
    
    def create(self, validated_data):

        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        

        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


    
