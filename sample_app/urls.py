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
# Al basename se le añadirá sufijo "-list" o "-detail" según que vista se quiera utilizar
router.register(r'countries', CountryViewSet, basename='rest_country_view_set')
router.register(r'colours', CatalogColourViewSet, basename='rest_cat_colours_view_set')

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
