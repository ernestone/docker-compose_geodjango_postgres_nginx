#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)

from rest_framework.serializers import SerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer, ModelSerializer

from .models import Country, CatalogColour


class CatelogColourSerializer(ModelSerializer):
    """ Class serializer for CatalogColour """

    class Meta:
        model = CatalogColour
        fields = '__all__'


class CountrySerializer(GeoFeatureModelSerializer):
    """ Clase serializador Country """
    colour = SerializerMethodField()

    class Meta:
        model = Country
        geo_field = 'border'
        fields = '__all__'

    def get_colour(self, obj):
        return obj.colour.hex
