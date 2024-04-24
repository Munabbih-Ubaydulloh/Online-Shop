from django.contrib import admin
from .models import User , Profile, Confirmation, UploadFile , ProfilePictures, Address 


admin.site.register(User)

admin.site.register(Profile)

admin.site.register(Confirmation)

admin.site.register(UploadFile)

admin.site.register(ProfilePictures)

