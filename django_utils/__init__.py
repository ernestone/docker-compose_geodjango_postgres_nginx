#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)
from django.contrib.gis.utils import LayerMapping


class CustomLayerMapping(LayerMapping):
    def __init__(self, *args, **kwargs):
        self.custom = kwargs.pop('custom', {})
        super(CustomLayerMapping, self).__init__(*args, **kwargs)

    def feature_kwargs(self, feature):
        kwargs = super(CustomLayerMapping, self).feature_kwargs(feature)
        kwargs.update(self.custom)
        return kwargs


def get_fields_model(a_model, pk=False):
    """
    Get fields of a model

    Args:
        a_model:
        pk:

    Returns:
        list
    """
    meta_model = a_model._meta
    return [fld.name for fld in meta_model.fields if not pk and fld != meta_model.pk]