#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)
import sys
import traceback

from django.views.debug import ExceptionReporter


class CustomExceptionReporter(ExceptionReporter):
    """ Fix problema al emitir error """

    def get_traceback_text(self):
        try:
            return super().get_traceback_text()
        except Exception as e:
            error_type, error_instance, exc_tb = sys.exc_info()

            error_msg = f"!AVISO! - No se ha podido generar el informe de Error por haber " \
                        f"saltado la excepción '{error_type}' \n\n" \
                        f"{''.join(traceback.format_exception(error_type, error_instance, exc_tb))}" \

            if hasattr(error_instance, "output"):
                error_msg += "\n\n" \
                             "Output: {}".format(error_instance.output)

            return error_msg
