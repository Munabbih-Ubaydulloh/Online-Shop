from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from django.utils import timezone

class User(AbstractBaseUser, PermissionsMixin):

    phone = models.CharField(unique=True, verbose_name="Telefon", max_length=16)
    activated_date = models.DateTimeField(blank=True, null=True, verbose_name="Aktivlashgan Vaqti")
    is_seller = models.BooleanField(default=False, verbose_name="Sotuvchilik holati")
    is_superuser = models.BooleanField(default=False, verbose_name="Superuser")
    is_staff = models.BooleanField(default=False, verbose_name='Staff')
    is_active = models.BooleanField(default=False, verbose_name='Aktivligi')

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


    def __str__(self) -> str:
        return str(self.phone)


class Confirmation(models.Model):
    ... 


class Profile(models.Model):

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, verbose_name="Ism", blank=True, null=True)
    last_name = models.CharField(max_length=50, verbose_name="Familiya", blank=True, null=True)
    email = models.EmailField(max_length=50, null=True, blank=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ro'yhatdan o'tgan vaqti")

    def full_name(self):

        return self.first_name + " " + self.last_name if self.first_name and self.last_name else self.phone

    def __str__(self) -> str:
        return self.full_name() + "'s Profile" if self.first_name and self.last_name else "Profile User with Phone " + self.user.phone 



class UploadFile(models.Model):

    file = models.FileField(upload_to='static/uploads/')


    def __str__(self) -> str:
        return self.id
    
    def url(self):

        return self.file.url if self.file else None


class ProfilePictures(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile_images")
    image = models.ForeignKey(UploadFile, on_delete=models.CASCADE)


    def __str__(self) -> str:
        return self.profile.user + " Images"


    def url(self):

        return self.file.url if self.file else None
    


class Address(models.Model):
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, verbose_name="Manzil sarlavhasi", blank=True, null=True)
    country = models.CharField(max_length=50, verbose_name="Mamlakat")
    province = models.CharField(max_length=50, verbose_name="Viloyat")
    district = models.CharField(max_length=50, verbose_name="Shahar / Tuman")
    street = models.CharField(max_length=50, verbose_name="Ko'cha nomi va uy raqami")
    zip_code = models.IntegerField(verbose_name="Pochta Indeksi")


    def __str__(self) -> str:
        return self.profile.user.full_name() + f" => {self.province} {self.district} {self.street}"
     



