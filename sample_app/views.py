from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django_filters import FilterSet
from djgeojson.views import GeoJSONLayerView
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from sample_app.serializers import CountrySerializer, BorderCountrySerializer, BboxCountrySerializer, \
    CatalogColourSerializer
from django_utils.auth_decorators import conditional_login_required
from django_utils import get_fields_model
from sample_app.models import Country, CatalogColour


# Vistas TEMPLATE
@conditional_login_required(
    login_url='login',
    redirect_field_name='next'
)
def map_view(request):
    """

    Args:
        request:

    Returns:
        HttpResponse
    """
    return render(request, 'map.html')


# Vistas REST-FRAMEWORK
class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = [SearchFilter]
    # Al usar SearchFilter con Postgres se puede utilizar 'Full text search' o 'tsvector + tsquery'
    # Mirar doc en 'https://docs.djangoproject.com/en/3.1/ref/contrib/postgres/search/'
    # Para definir tipos de busqueda según campo mirar 'https://www.django-rest-framework.org/api-guide/filtering/#searchfilter'
    search_fields = ('=code', '@name', '@name_iso_country', '=code_iso3_country',
                     #'@wikidata__descriptions__en__value', #TODO search wiki document
                     '@economy', '@income_grp', '@continent', '@region_un', '@subregion', '@region_wb')

    def get_queryset(self):
        return super(CountryViewSet, self).get_queryset()


class BorderCountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = BorderCountrySerializer
    filter_backends = [SearchFilter]
    # Al usar SearchFilter con Postgres se puede utilizar 'Full text search' o 'tsvector + tsquery'
    # Mirar doc en 'https://docs.djangoproject.com/en/3.1/ref/contrib/postgres/search/'
    # Para definir tipos de busqueda según campo mirar 'https://www.django-rest-framework.org/api-guide/filtering/#searchfilter'
    search_fields = ('=code', '@name', '@name_iso_country', '=code_iso3_country')


class BboxCountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = BboxCountrySerializer
    filter_backends = [SearchFilter]
    # Al usar SearchFilter con Postgres se puede utilizar 'Full text search' o 'tsvector + tsquery'
    # Mirar doc en 'https://docs.djangoproject.com/en/3.1/ref/contrib/postgres/search/'
    # Para definir tipos de busqueda según campo mirar 'https://www.django-rest-framework.org/api-guide/filtering/#searchfilter'
    search_fields = ('=code', '@name')


class CatColourFilterSet(FilterSet):
    """ Class filter for Colours """

    class Meta:
        model = CatalogColour
        fields = {'id': ['exact', 'in'],
                  'hex': ['exact', 'in'],
                  'name': ['exact', 'in', 'icontains']}


class CatalogColourViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CatalogColourSerializer
    queryset = CatalogColour.objects.all()
    filterset_class = CatColourFilterSet
    

# Vistas GEOJSONLAYER ()
# !!!ATENTION!!! NO USADA EN EL SAMPLE - SOLO EJ. A MODO DEMO EN DEBUG
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
