#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)
from rest_framework_gis.serializers import ModelSerializer, GeoFeatureModelSerializer


class DynamicFieldsModelSerializerMixin(object):
    """
    A Mixon Serializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializerMixin, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            if hasattr((meta := getattr(self, 'Meta')), 'geo_field'):
                allowed.add(getattr(meta, 'geo_field'))

            existing = set(getattr(self, 'fields'))
            for field_name in existing - allowed:
                getattr(self, 'fields').pop(field_name)


class DynamicFieldsGeoModelSerializer(DynamicFieldsModelSerializerMixin, GeoFeatureModelSerializer):
    """
    A GeoModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """
    pass


class DynamicFieldsModelSerializer(DynamicFieldsModelSerializerMixin, ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """
    pass
