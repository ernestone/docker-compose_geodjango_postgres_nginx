#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)
from tempfile import NamedTemporaryFile
from urllib.request import urlretrieve
from urllib.error import HTTPError
import overpy

URL_BASE_OSM = 'http://download.openstreetmap.fr/polygons/'
REGIONS = ('africa', 'asia', 'central-america', 'europe', 'north-america', 'oceania', 'russia', 'south-america')


def osm_limits_country(n_country, bbox=None):
    """

    Args:
        n_country:
        bbox (tuple=None): (lat_south, lon_west, lat_north, lon_east)

    Returns:
        overpy.Result
    """
    api = overpy.Overpass()

    if bbox:
        str_bb = str(bbox)
    else:
        str_bb = ''

    res = api.query(
        f"area['name:en'='{n_country}']->.country;"
        f"rel['name:en'='{n_country}']['type'='boundary']['admin_level'='2'];"
        f"(way(r)['maritime' != 'yes']{str_bb};way(area.country)['natural'='coastline']{str_bb};);"
        f"out geom;")

    return res


def request_poly_file_country(n_country, region=None, filename=None):
    """
    
    Args:
        n_country (str):
        region (str):
        filename (str):

    Returns:
        request
    """
    if region:
        chk_regions = (region, )
    else:
        chk_regions = REGIONS

    for r in chk_regions:
        try:
            file_path, resp = urlretrieve(f'{URL_BASE_OSM}/{r}/{n_country.lower()}.poly', filename=filename)

            return file_path
        except HTTPError as exc:
            pass

    
def osm_poly_file_country(n_country, region=None):
    """

    Args:
        n_country (str):
        region (str=None):

    Returns:
        lines_file (list): list strings with osm definition
    """
    if file_path := request_poly_file_country(n_country, region=region):
        with open(file_path) as file:
            return file.readlines()
