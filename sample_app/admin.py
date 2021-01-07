from django.contrib import admin
from django.contrib.admin import ModelAdmin
from leaflet.admin import LeafletGeoAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import Country, CatalogColour

# Register your models here.


@admin.register(CatalogColour)
class CatalogColourAdmin(ModelAdmin):
    list_display = ('name', 'hex')
    search_fields = ('name', 'hex')
    ordering = ('name',)


@admin.register(Country)
class CountryAdmin(LeafletGeoAdmin, SimpleHistoryAdmin):
    list_display = ('code', 'name', 'name_iso_country', 'code_iso3_country')
    search_fields = ('code', 'name__startswith')
    ordering = ('name',)
