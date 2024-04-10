from django.urls import path 
from .views import (
    SignUpView , AllUsersView
)

urlpatterns = [
    
    path("sign-up/", SignUpView.as_view(), name="user-register"),
    path("all/", AllUsersView.as_view(), name="users"),
    

]