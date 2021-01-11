#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)
import os
import sys
from logging import getLogger
import wikipediaapi

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Polygon
from django.db.models import Q, ProtectedError
from django.utils.translation import get_language

from common_utils.misc import rows_csv, first_num_from_str, brewer_colour, json_from_url
from django_base import settings
from sample_app.models import get_or_set_country, get_or_set_colour, Country, CatalogColour

URL_JSON_WIKI_COUNTRY = 'https://www.wikidata.org/w/api.php?' \
                        'action=wbgetentities&ids={id_country}&' \
                        'props=aliases|descriptions|sitelinks&sitefilter={language}wiki&' \
                        'languages={language}&format=json'

TEMP_NOM_PROC_SINCRO = 'sincronización de {n_obj} (fichero={file_name})'
LOGGER = getLogger('sample.logs')
FILE_SINC_COLOURS = 'colours.csv'
FILE_SINC_COUNTRIES = 'countries.csv'
PATH_GEOJSON_COUNTRIES = os.path.join(settings.DATA_DIR_SAMPLE, 'countries.geojson')


# --- LOAD from files ---
def remove_objects_excluded(object, exclude_q_filter):
    l_errors = []
    for reg_to_remove in object.objects.exclude(exclude_q_filter):
        r_desc = str(reg_to_remove)
        try:
            reg_to_remove.delete()
        except ProtectedError as exc:
            LOGGER.error(msg_err := f'No se ha podido borrar el registro {object} {r_desc}', exc_info=sys.exc_info())
            l_errors.append(msg_err)
        else:
            LOGGER.info(f'!ATENCIÓN! - Se ha borrado el {object} {r_desc}')

    return l_errors


def load_file_sincro_countries(path_dir=settings.DATA_DIR_SAMPLE, remove=False):
    """
    Carga colores a partir fichero FILE_SINC_COUNTRIES

    Args:
        remove:
        path_dir:

    Returns:
        l_errors = []
    """
    l_errors = []

    path_csv = os.path.join(path_dir, FILE_SINC_COUNTRIES)

    LOGGER.info(f'Inicio {(nom_proc := TEMP_NOM_PROC_SINCRO.format(n_obj="Countries", file_name=FILE_SINC_COUNTRIES))}')
    mapping_cols_flds = {'code': 'code',
                         'name': 'name',
                         'geometry_n': 'bb_lat_n',
                         'geometry_o': 'bb_lon_w',
                         'geometry_s': 'bb_lat_s',
                         'geometry_e': 'bb_lon_e'}

    q_filt_remove = None

    for row in rows_csv(path_csv, header=True, sep=';', encoding='cp1252'):
        map_row = {mapping_cols_flds.get(k): v for k, v in row.items()}

        code_country = map_row.get('code')
        name_country = map_row.get('name')

        if remove:
            if code_country:
                q_filt = Q(code=code_country)
            else:
                q_filt = Q(name=name_country)

            if q_filt_remove:
                q_filt_remove = q_filt_remove | q_filt
            else:
                q_filt_remove = q_filt

        try:
            extra_atts = {}
            vals_bbox_coords = [num_val for k in ('bb_lon_w', 'bb_lat_s', 'bb_lon_e', 'bb_lat_n')
                                if (num_val := first_num_from_str(map_row.get(k)))]
            if len(vals_bbox_coords) == 4:
                extra_atts['bbox'] = Polygon.from_bbox(vals_bbox_coords)

            country_tratada, created = get_or_set_country(code_country=code_country, name_country=name_country,
                                                          update=True, **extra_atts)
        except Exception:
            LOGGER.error(msg_err := f'No se ha podido tratar el {Country} para los datos [{",".join(row.values())}]',
                         exc_info=sys.exc_info())
            l_errors.append(msg_err)
        else:
            LOGGER.debug(f'Country tratado: {country_tratada}')

    if q_filt_remove:
        l_errors.extend(remove_objects_excluded(Country, q_filt_remove))

    LOGGER.info(f'Fin {nom_proc}')

    return l_errors


def load_geojson_countries(path_geojson=PATH_GEOJSON_COUNTRIES):
    """
    Load from geojson countries from https://www.naturalearthdata.com/
    Args:
        path_geojson:

    Returns:

    """
    try:
        ds = DataSource(path_geojson)
        lyr = next((l for l in ds))
    except Exception:
        LOGGER.warning(f'Impossible to load countries from "{path_geojson}"')
        return

    feat_iso2 = lambda f: iso2 if (iso2 := f.get('ISO_A2')) and iso2 != '-99' else f.get('WB_A2')
    feat_iso3 = lambda f: iso3 if (iso3 := f.get('ISO_A3_EH')) and iso3 != '-99' else f.get('WB_A3')

    code_lang, region_lang = get_language().split('-')
    wiki_en = wikipediaapi.Wikipedia()
    wiki_lang = wikipediaapi.Wikipedia(code_lang)

    for feat in (f for f in lyr if feat_iso2(f) != '-99'):
        cat_colour, created = get_or_set_colour(*brewer_colour(feat.get('MAPCOLOR9'), number=9))

        wikidata_id = feat.get('WIKIDATAID')
        wikidata = json_from_url(URL_JSON_WIKI_COUNTRY.format(id_country=wikidata_id,
                                                              language=code_lang))
        site_links = next(iter(wikidata.get('entities', {}).get(wikidata_id, {}).get('sitelinks', {}).values()), {})
        name_country = site_links.get('title', name_en := feat.get('NAME_EN'))
        wiki_page_country = wiki_lang.page(name_country)
        if not wiki_page_country.exists():
            wiki_page_country = wiki_en.page(name_en)

        country, created = get_or_set_country(
            code_country=feat_iso2(feat),
            name_country=name_country,
            pol_border=feat.geom.geos,
            code_iso3_country=feat_iso3(feat),
            name_iso_country=feat.get('NAME'),
            colour=cat_colour,
            wikidata=wikidata,
            wikipedia=wiki_page_country.summary,
            pop_est=feat.get('POP_EST'),
            gdp_md_est=feat.get('GDP_MD_EST'),
            economy=feat.get('ECONOMY'),
            income_grp=feat.get('INCOME_GRP'),
            continent=feat.get('CONTINENT'),
            region_un=feat.get('REGION_UN'),
            subregion=feat.get('SUBREGION'),
            region_wb=feat.get('REGION_WB'),
            update=True,
            idioma='en'
        )

        LOGGER.debug(f'Country {country} loaded')


def load_file_sincro_colours(path_dir=settings.DATA_DIR_SAMPLE, remove=False):
    """
    Carga colores a partir fichero FILE_SINC_COLOURS

    Args:
        remove:
        path_dir:

    Returns:
        l_errors = []
    """
    l_errors = []

    path_csv = os.path.join(path_dir, FILE_SINC_COLOURS)

    LOGGER.info(f'Inicio {(nom_proc := TEMP_NOM_PROC_SINCRO.format(n_obj="Colours", file_name=FILE_SINC_COLOURS))}')
    mapping_cols_flds = {'color cod': 'id',
                         'color name': 'name',
                         'hex rgb': 'hex'}

    q_filt_remove = None

    for row in rows_csv(path_csv, header=True, sep=';', encoding='cp1252'):
        map_row = {mapping_cols_flds.get(k): v for k, v in row.items()}

        id_colour = map_row.get('id')

        if remove:
            q_filt = Q(id=id_colour)

            if q_filt_remove:
                q_filt_remove = q_filt_remove | q_filt
            else:
                q_filt_remove = q_filt

        try:
            colour_tratado, created = get_or_set_colour(hex=map_row.get('hex', '').strip(),
                                                        set_name=map_row.get('name', '').strip())
        except Exception:
            LOGGER.error(msg_err := f'No se ha podido tratar el {CatalogColour} para los datos '
                                    f'[{",".join(row.values())}]',
                         exc_info=sys.exc_info())
            l_errors.append(msg_err)
        else:
            LOGGER.debug(f'Colour tratado: {colour_tratado}')

    if q_filt_remove:
        l_errors.extend(remove_objects_excluded(CatalogColour, q_filt_remove))

    LOGGER.info(f'Fin {nom_proc}')

    return l_errors


def load_countries(apps=None, schema_editor=None):
    # Initial load countries
    load_geojson_countries()


if __name__ == '__main__':
    import fire

    fire.Fire({
        load_file_sincro_countries.__name__, load_file_sincro_countries,
        load_file_sincro_colours.__name__, load_file_sincro_colours
    })
