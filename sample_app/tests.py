from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from django_base.settings import AUTH_ACTIVATED
from sample_admin_app.models import UserSample
from sample_app.load_data import load_file_sincro_colours, load_file_sincro_countries, load_geojson_countries
from sample_app.management.commands.load_data_dir import load_data
from sample_app.models import custom_update_change_reason, Country
from sample_app.views import CountryViewSet


# Create your tests here.
SAMPLE_PSW = 'sample_123zxc'
SAMPLE_MAIL = 'sample@mail.com'


class LoadDataSampleTestCase(TestCase):
    fixtures = []

    def test_command_load(self):
        load_data()

    def test_sincro_colours(self):
        load_file_sincro_colours()

    def test_sincro_countries(self):
        load_file_sincro_countries()

    def test_load_geojson_countries(self):
        load_geojson_countries()


class SampleAppUtilsTestCase(TestCase):
    fixtures = []

    def test_custom_update_change(self):
        load_file_sincro_countries()
        t = Country.objects.get(id=1)
        custom_update_change_reason(t, "Esto es una prueba")


class RestViewsTestCase(TestCase):
    fixtures = []
    factory = APIRequestFactory()

    def setUp(self):
        if AUTH_ACTIVATED and not UserSample.objects.exists():
            UserSample.objects.create_superuser(email=SAMPLE_MAIL, password=SAMPLE_PSW)
        if not Country.objects.exists():
            load_file_sincro_countries()

    def test_request_country(self):
        assert resp_for_country(1)


def resp_for_country(id_country):
    user = UserSample.objects.get(email=SAMPLE_MAIL)
    view = CountryViewSet.as_view({'get': 'list'})
    req = APIRequestFactory().get(f'/rest/countries/{id_country}', format='application/json')
    if AUTH_ACTIVATED:
        force_authenticate(req, user=user)
    return view(req)
