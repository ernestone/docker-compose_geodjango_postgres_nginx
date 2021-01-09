#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 16/09/20
#  Copyright (c)
from django.urls import path, include
from rest_framework import routers

from django_base.settings import DEBUG
from .views import map_view, CountryViewSet, CatalogColourViewSet, MapLayerCountries

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'colours', CatalogColourViewSet)

urlpatterns = [
    # Vistas DATA API REST-FRAMEWORK
    path(r'rest/', include(router.urls)),
]

if DEBUG:
    urlpatterns.extend(
        [
            # Vistas GEOJSON via
            path(r'countries.geojson', MapLayerCountries.as_view(), name='countries_geojson'),

            # Vistas django-templates MAPA
            path(r'map/', map_view, name='map'),
        ]
    )
