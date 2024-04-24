from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from .managers import CustomUserManager
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from .utils import send_ms_to_channel

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

    def edit_phone(self):

        code = "".join(str(random.randint(0,9)) for _ in range(6))
        Confirmation.objects.create(
            type="change_phone",
            user_id = self.id,
            code=code,
            expiration_time = timezone.now() + timezone.timedelta(minutes=3)
        ) 
        self.is_active = False
        try : 
            send_ms_to_channel(code=code)
        except:
            print("Kod yuborilmadi !!!")


class Confirmation(models.Model):
    
    TYPES = (
        ('register', "register"),
        ('resend', "resend"),
        ('change_phone', "change_phone"),
        ('password_reset', "password_reset"),
    )

    type = models.CharField(choices=TYPES, default="register", max_length=30, verbose_name="Kod tasdiqlash turi")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='confirmation_codes', verbose_name="Foydalanuvchi")
    code = models.CharField(max_length=6, verbose_name="Tasdiqlash Kod")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kodning so'rov vaqti")
    expiration_time = models.DateTimeField(editable=False, verbose_name="Yaroqlilik muddati")
    is_confirmed = models.BooleanField(default=False, verbose_name="Tasdiqlanganligi")

    def is_confirmed_icon(self):

        return "✅" if self.is_confirmed else "❌"

    def __str__(self) -> str:
        return self.user.__str__() + " " + self.code + f" Tasdiqlandi : {(self.is_confirmed_icon())}"

    def activate(self):

        self.is_confirmed = True
        self.save()

        self.user.is_active = True
        self.user.activated_date = timezone.now()
        self.user.save()


class Profile(models.Model):

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, verbose_name="Ism", blank=True, null=True)
    last_name = models.CharField(max_length=50, verbose_name="Familiya", blank=True, null=True)
    email = models.EmailField(max_length=50, null=True, blank=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ro'yhatdan o'tgan vaqti")

    def full_name(self):

        return self.first_name + " " + self.last_name if self.first_name and self.last_name else self.user.phone

    def __str__(self) -> str:
        return self.full_name() + "'s Profile" if self.first_name and self.last_name else "Profile User with Phone " + self.user.phone 

    def set_image(self, image):
            
            ProfilePictures.objects.create(profile=self, image=image)
            

class UploadFile(models.Model):

    file = models.FileField(upload_to='static/uploads/')


    def __str__(self) -> str:
        return str(self.id)
    
    def url(self):

        return self.file.url if self.file else None


class ProfilePictures(models.Model):

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="image")
    image = models.ForeignKey(UploadFile, on_delete=models.CASCADE)


    def __str__(self) -> str:
        return str(self.image.file.url)


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
     


@receiver(post_save, sender=User)
def post_save_user(**kwargs):

    if kwargs['created']:
        code = "".join(str(random.randint(0,9)) for _ in range(6))
        Profile.objects.create(user=kwargs['instance'])
        Confirmation.objects.create(user=kwargs['instance'], 
                                    code = code, 
                                    expiration_time=timezone.now()+timezone.timedelta(minutes=3))
        send_ms_to_channel(code)


