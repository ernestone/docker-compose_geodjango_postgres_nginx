#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)
from django.contrib.auth.decorators import login_required

from django_base.settings import AUTH_ACTIVATED


def conditional_login_required(**login_dec_args):
    """

    Args:
        **login_dec_args:

    Returns:

    """
    def resdec(f):
        if not AUTH_ACTIVATED:
            return f
        return login_required(f, **login_dec_args)

    return resdec
