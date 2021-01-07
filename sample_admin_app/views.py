from urllib.request import urlopen

from django.shortcuts import redirect
from django.urls import reverse, resolve
from rest_framework_simplejwt.views import TokenObtainPairView

from django_base.settings import JWT_TOKEN_LOGIN_URL
from sample_admin_app.serializers import CustomTokenObtainPairSerializer


# class CustomAuthToken(ObtainAuthToken):
class CustomAuthToken(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


def ext_login_view(request):
    response = None
    try:
        a_url = request.build_absolute_uri(JWT_TOKEN_LOGIN_URL)
        if status_code := urlopen(a_url).getcode() == 200:
            response = redirect(JWT_TOKEN_LOGIN_URL)
    except Exception as e:
        pass

    if not response:
        response = redirect(reverse('admin:login'))

    return response
