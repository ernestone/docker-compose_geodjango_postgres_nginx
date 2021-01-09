#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)
from rest_framework.fields import BooleanField, SerializerMethodField
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from sample_admin_app.models import UserSample
from sample_app.serializers import BboxCountrySerializer


class UserSampleSerializer(ModelSerializer):
    """ Clase serializador UserSample """
    is_admin = BooleanField(read_only=True, required=False) # Ref to property 'UserSample.is_admin'
    countries = SerializerMethodField()

    def get_countries(self, user):
        return BboxCountrySerializer(user.get_countries(), many=True, fields=('id', 'code', 'name')).data

    class Meta:
        model = UserSample
        exclude = ['password']
        depth = 1


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """

    """
    def get_token(self, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['firt_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_admin'] = user.is_admin
        token['countries'] = {pa.pk: pa.name for pa in user.get_countries()}

        return token
