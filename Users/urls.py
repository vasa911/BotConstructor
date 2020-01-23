from django.urls import path

from .views import *

urlpatterns = [
    path('', base_view, name='base_view_url'),
    path('signUp/', UserRegistration.as_view(), name='user_registration_url'),
    path('signIn/', UserAuthentication.as_view(),
         name='user_authentication_url'),
    path('updateProfile/', UpdateProfile.as_view(), name='update_profile_url'),
    # path('updateImage/', UpdateImage.as_view(), name='update_image_url'),
    path('deleteUser/', UserDelete.as_view(), name='user_delete_url'),
    path('profile/', ProfileView.as_view(), name='profile_url'),
    path('logOut', UserLogout.as_view(), name='user_logout_url'),
    path('deleteUser', UserDelete.as_view(), name='user_delete_url')
]
