#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)

from rest_framework.serializers import SerializerMethodField
from django_utils.serializers import DynamicFieldsGeoModelSerializer, DynamicFieldsModelSerializer

from .models import Country, CatalogColour


class CatalogColourSerializer(DynamicFieldsModelSerializer):
    """ Class serializer for CatalogColour """

    class Meta:
        model = CatalogColour
        fields = '__all__'


class CountrySerializer(DynamicFieldsModelSerializer):
    """ Clase serializador Country """
    class Meta:
        model = Country
        exclude = ('border', 'bbox')


class BorderCountrySerializer(DynamicFieldsGeoModelSerializer):
    """ Clase serializador Country """
    colour = SerializerMethodField()

    class Meta:
        model = Country
        geo_field = 'border'
        fields = ('id', 'code', 'name', 'colour', 'name_iso_country', 'code_iso3_country')

    def get_colour(self, obj):
        return obj.colour.hex


class BboxCountrySerializer(DynamicFieldsGeoModelSerializer):
    """ Clase serializador Country """

    class Meta:
        model = Country
        geo_field = 'bbox'
        fields = ('id', 'code', 'name')
