'''
Created on Oct 27, 2017

@author: agutierrez
'''
from madmex.management.base import AntaresBaseCommand
from madmex.models import LandsatCatalog


class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--filename', nargs=1)
        parser.add_argument('--path', nargs=1, type=int)
        parser.add_argument('--row', nargs=1, type=int)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        row = options['row'][0]
        path = options['path'][0]
        with open(filename, 'w') as list_file:
            for scene in LandsatCatalog.objects.filter(row=row, path=path):
                list_file.write('%s\n' % scene.landsat_product_id)
            list_file.close()