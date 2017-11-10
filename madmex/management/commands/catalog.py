'''
Created on Oct 27, 2017

@author: agutierrez
'''
import csv
import logging

from madmex.management.base import AntaresBaseCommand
from madmex.models import LandsatCatalog, LansatAWS
from madmex.util import create_filename, INDEXES, SCENES_MEXICO


LOGGER = logging.getLogger(__name__)


class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--directory', nargs=1)

    def handle(self, *args, **options):
        
        directory = options['directory'][0]
    
        
        with open(directory, 'rb') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                ob = LansatAWS( product_id = row[0],
                                entity_id = row[1],
                                acquisitionDate = row[2],
                                cloudCover = row[3],
                                processingLevel = row[4],
                                path = row[5],
                                row = row[6],
                                min_lat = row[7],
                                min_lon = row[8],
                                max_lat = row[9],
                                max_lon = row[10],
                                download_url = row[11])
                
                ob.save()
                