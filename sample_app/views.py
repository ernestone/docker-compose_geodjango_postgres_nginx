from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import TemplateView
from django_filters import FilterSet
from djgeojson.views import GeoJSONLayerView
from rest_framework import viewsets

from sample_app.models import Country, CatalogColour
from sample_app.serializers import CountrySerializer, CatelogColourSerializer
from django_utils import get_fields_model


# Vistas TEMPLATE
class MapView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    redirect_field_name = 'next'
    redirect_authenticated_user = True
    extra_context = {'next': 'map'}


# Vistas REST-FRAMEWORK
class CountryFilterSet(FilterSet):
    """ Class filter for Countries """

    class Meta:
        model = Country
        fields = {'id': ['exact', 'in'],
                  'code': ['exact', 'in'],
                  'name': ['exact', 'in']}


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filterset_class = CountryFilterSet

    def get_queryset(self):
        return super(CountryViewSet, self).get_queryset()

    def get_serializer_class(self):
        return super(CountryViewSet, self).get_serializer_class()


class CatalogColourViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CatalogColour.objects.all()
    serializer_class = CatelogColourSerializer
    

# Vistas GEOJSONLAYER
class BaseGeo(LoginRequiredMixin, GeoJSONLayerView):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    precision = 4
    simplify = 0.5
    bbox_auto = True
    geometry_field = 'geometry'
    title_field = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        mapping_fields = {fn: fn for fn in get_fields_model(self.model)}
        if self.title_field:
            mapping_fields[self.title_field] = 'title'

        self.properties = mapping_fields


class MapLayerCountries(BaseGeo):
    model = Country
    geometry_field = 'border'
    title_field = 'name'
    join_fields = {'colour': 'hex'}
