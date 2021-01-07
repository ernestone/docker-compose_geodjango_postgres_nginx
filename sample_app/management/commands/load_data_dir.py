#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 16/09/2020
#  Copyright (c)
import inspect
from logging import getLogger

from django_base import settings
from django.core.management import BaseCommand, CommandError

from sample_app.load_data import load_file_sincro_colours, load_file_sincro_countries

LOGGER = getLogger('sample.errors')
LOGGER_INFO = getLogger('sample.logs')


def load_data(path_data=settings.DATA_DIR_SAMPLE, name_proc='load_sample_data', remove=False):
    """

    Args:
        path_data (str=settings.DATA_DIR_SAMPLE):
        name_proc (str='load_sample_data'):
        remove (bool=False):

    Returns:

    """
    LOGGER_INFO.info(f'Inicio proceso manual de sincronización ({name_proc})')

    l_errors = []

    l_errors.extend(load_file_sincro_colours(path_data, remove=remove))
    l_errors.extend(load_file_sincro_countries(path_data, remove=remove))

    if l_errors:
        str_errors = "\n\t -> ".join(l_errors)
        LOGGER_INFO.info(f'Se han encontrado errores en el proceso de sincronización: \n '
                         f'{str_errors}')
    LOGGER_INFO.info(f'Fin proceso manual de sincronización ({name_proc})')


class Command(BaseCommand):
    nom_proc = 'proceso de carga a partir ficheros sincronización datos Sample'
    help = f'Lanza el {nom_proc}'

    def add_arguments(self, parser):
        parser.add_argument('--path_data', type=str)
        parser.add_argument('--name_proc', type=str)
        parser.add_argument('--update', action='store_true')

    def handle(self, *args, **options):
        try:
            n_params_func = inspect.signature(load_data).parameters
            params = {k: v for k, v in options.items()
                      if k in n_params_func and v}

            LOGGER_INFO.debug(params)
            load_data(**params)
        except Exception:
            LOGGER.exception(f'Error al ejecutar el {self.nom_proc}')
            raise CommandError(f'El {self.nom_proc} no se ha podido efectuar')
        else:
            LOGGER_INFO.info(msg_info := f'{self.nom_proc.capitalize()} efectuado correctamente')
            self.stdout.write(self.style.SUCCESS(msg_info))


if __name__ == '__main__':
    import fire

    fire.Fire({
        load_data.__name__: load_data
    })
