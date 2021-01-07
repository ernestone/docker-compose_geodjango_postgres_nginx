#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 16/09/20
#  Copyright (c)
from django.urls import path, include, reverse
from .views import CustomAuthToken, ext_login_view
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Vistas AUTH LOGIN
    path(r'', ext_login_view, name='jwt_token_login'),

    path(r'rest/',
         include([
             path(r'jwt-token-auth/', CustomAuthToken.as_view(), name='custom_token_obtain_pair'),
             path(r'jwt-token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
         ]))
]
