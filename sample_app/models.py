import re

from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.core.validators import RegexValidator
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords
from simple_history.utils import get_history_manager_for_model

from common_utils.misc import get_country_info, random_brewer_colour
from django_utils.geo import get_multi_polygon


class CatalogColour(models.Model):
    """ Cataleg colours """
    id = models.AutoField(primary_key=True)
    hex = models.CharField(max_length=7,
                           default=f'#000000',
                           validators=[RegexValidator('^#[A-F0-9]{6}$',
                                                      message='Enter a valid hexfigure: e.g. "ff0022"',
                                                      flags=re.IGNORECASE)])
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name if self.name else self.default_colour_name()

    @property
    def red(self):
        return int(f'0x{self.hex[1:3]}', 0)

    @property
    def green(self):
        return int(f'0x{self.hex[3:5]}', 0)

    @property
    def blue(self):
        return int(f'0x{self.hex[5:7]}', 0)

    def default_colour_name(self):
        return f'{self.hex} RGB({self.red:03d},{self.green:03d},{self.blue:03d})'

    class Meta:
        db_table = 'catalog_colour'


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100, unique=True)
    name_iso_country = models.CharField(max_length=100, unique=True, blank=True, null=True)
    code_iso3_country = models.CharField(max_length=3, unique=True, blank=True, null=True)

    wikidata = models.JSONField(blank=True, null=True)
    pop_est = models.IntegerField(blank=True, null=True)
    gdp_md_est = models.IntegerField(blank=True, null=True)
    economy = models.CharField(max_length=100, blank=True, null=True)
    income_grp = models.CharField(max_length=100, blank=True, null=True)
    continent = models.CharField(max_length=100, blank=True, null=True)
    region_un = models.CharField(max_length=100, blank=True, null=True)
    subregion = models.CharField(max_length=100, blank=True, null=True)
    region_wb = models.CharField(max_length=100, blank=True, null=True)

    border = models.MultiPolygonField(blank=True, null=True)
    bbox = models.PolygonField(blank=True, null=True)

    colour = models.ForeignKey(CatalogColour, models.PROTECT, blank=True, null=True)

    history = HistoricalRecords(table_name=f'historic_countries')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'country'
        verbose_name_plural = 'Countries'


def get_or_set_colour(hex, set_name=None):
    """

    Args:
        hex (str=None): color hexadecimal en este formato '#FFFFFF'
        set_name:

    Returns:
        models.CatalogColour, bool
    """
    colour_tratado = None
    created_or_updated = False
    objs_colour = CatalogColour.objects
    qs_colour = objs_colour.filter(hex=hex)

    vals_flds = {}
    if set_name:
        vals_flds['name'] = set_name

    if not qs_colour and vals_flds:
        colour_tratado = objs_colour.create(hex=hex, **vals_flds)
        created_or_updated = True
    elif qs_colour:
        colour_tratado = qs_colour.get()

        if vals_flds:
            for fld, val in vals_flds.items():
                setattr(colour_tratado, fld, val)
            colour_tratado.save(update_fields=vals_flds)
            created_or_updated = True

    return colour_tratado, created_or_updated


@receiver(pre_save, sender=CatalogColour)
def handler_pre_save_colour(sender, instance=None, **kwargs):
    """

    Args:
        sender (CatalogColour):
        instance (CatalogColour):
        **kwargs:

    Returns:

    """
    if not instance.name:
        instance.name = instance.default_colour_name()


def random_colour():
    """
    Retorna un CatalogColour random

    Returns:
        CatalogColour
    """
    cat_colour, db_updated = get_or_set_colour(*random_brewer_colour())
    return cat_colour


def custom_update_change_reason(instance, reason):
    attrs = {}
    model = type(instance)
    manager = instance if instance.id is not None else model
    history = get_history_manager_for_model(manager)
    for field in (fld for fld in instance._meta.fields if fld.primary_key):
        attrs[field.attname] = getattr(instance, field.attname)

    if record := history.filter(**attrs).order_by("-history_date").first():
        record.history_change_reason = reason
        record.save()


def get_or_set_country(code_country=None, name_country=None, pol_border=None, idioma='en',
                       update=False, **extra_atts):
    """

    Args:
        code_country (str=None):
        name_country (str=None):
        pol_border (GEOSGeometry=None):
        idioma (str=None):
        update (bool=False):
        **extra_atts:  extra attributes for the country

    Returns:
        Country
    """
    created = False

    objs_country = Country.objects

    q_filter = None
    if name_country:
        q_filter = Q(name=name_country)
    if code_country:
        if q_filter:
            q_filter = q_filter | Q(code=code_country)
        else:
            q_filter = Q(code=code_country)

    qs_country = objs_country.filter(q_filter)
    if not qs_country:
        if not code_country:
            code_country = name_country[:5].upper()

        country_tratada = objs_country.create(
            code=code_country,
            name=name_country)
        created = True
    else:
        country_tratada = qs_country.get()

    if update or created:
        new_vals = extra_atts

        if pol_border:
            new_vals['border'] = get_multi_polygon(pol_border)

        if not any(nf in new_vals for nf in ('code_iso3_country', 'name_iso_country', 'border')):
            country, nom_country, limite_geojson, country_info = get_country_info(name_country, idioma)
            if country:
                new_vals['code_iso3_country'] = country.alpha_3
                if nom_country:
                    new_vals['name_iso_country'] = nom_country
                if not pol_border and limite_geojson:
                    new_vals['border'] = get_multi_polygon(GEOSGeometry(limite_geojson))

        for fld, val in new_vals.items():
            setattr(country_tratada, fld, val)

        country_tratada.save()

    return country_tratada, created


@receiver(pre_save, sender=Country)
def handler_pre_save_country(sender, instance=None, **kwargs):
    """

    Args:
        sender (Country):
        instance (Country):
        **kwargs:

    Returns:

    """
    if not instance.colour:
        instance.colour = random_colour()
    if instance.border and not instance.bbox:
        instance.bbox = instance.border.envelope
