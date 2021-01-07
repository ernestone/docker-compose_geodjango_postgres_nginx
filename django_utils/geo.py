#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)
from django.contrib.gis.gdal import SpatialReference, CoordTransform, OGRGeometry
from django.contrib.gis.geos import MultiPolygon, Polygon


def geos_point_utm(x_geom, y_geom, datum, utm_zone, hemisphere='south'):
    """
    GEt GEOSGeometry (GEOSPoint)
    Args:
        x_geom:
        y_geom:
        datum:
        utm_zone:
        hemisphere:

    Returns:

    """
    srs = SpatialReference(f'+proj=utm +zone={utm_zone} +{hemisphere} '
                           f'+ellps={datum} +datum={datum} +units=m +no_defs')
    ct = CoordTransform(srs, SpatialReference('4326'))
    pt = OGRGeometry(f'POINT ({x_geom} {y_geom})')
    pt.transform(ct)
    return pt.geos


def parse_poly_osm_file(lines):
    """
        Parse an Osmosis polygon filter file.

        Accept a sequence of lines from a polygon file, return a django.contrib.gis.geos.MultiPolygon object.

        http://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format

        Adapted from http://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Python_Parsing
    """
    in_ring = False
    coords = []
    ring = []

    for (index, line) in enumerate(lines):
        if index == 0:
            # first line is junk.
            continue

        elif in_ring and line.strip() == 'END':
            # we are at the end of a ring, perhaps with more to come.
            in_ring = False

        elif in_ring:
            # we are in a ring and picking up new coordinates.
            ring.append(list(map(float, line.split())))

        elif not in_ring and line.strip() == 'END':
            # we are at the end of the whole polygon.
            break

        elif not in_ring and line.startswith('!'):
            # we are at the start of a polygon part hole.
            coords[-1].append([])
            ring = coords[-1][-1]
            in_ring = True

        elif not in_ring:
            # we are at the start of a polygon part.
            coords.append([[]])
            ring = coords[-1][0]
            in_ring = True

    return MultiPolygon(*(Polygon(*polycoords) for polycoords in coords))


def get_multi_polygon(geos_geom):
    """

    Args:
        geos_geom (django.contrib.gis.geos.geometry.GEOSGeometry):

    Returns:
        MultiPolygon
    """
    if geos_geom.geom_type == 'Polygon':
        return MultiPolygon(geos_geom)
    else:
        return geos_geom
