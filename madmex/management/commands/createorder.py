'''
Created on Oct 27, 2017

@author: agutierrez
'''
import json
import logging
import time

from madmex.management.base import AntaresBaseCommand
from madmex.models import LandsatCatalog
from madmex.remote import UsgsApi


logger = logging.getLogger(__name__)

OLI_TIRS = 'olitirs8_collection'
ETM_PLUS = 'etm7_collection'
TM5 = 'tm5_collection'
TM4 = 'tm4_collection'


class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--path', nargs=1, type=int)
        parser.add_argument('--row', nargs=1, type=int)

    def handle(self, *args, **options):
        row = options['row'][0]
        path = options['path'][0]
        api = UsgsApi()
        scenes = LandsatCatalog.objects.filter(row=row, path=path, sensor='LANDSAT_TM')[:7]

        inputs = []
        
        collection = TM4
        products = ['sr', 'pixel_qa']
        

        for scene in scenes:
            print scene.landsat_product_id
            inputs.append(scene.landsat_product_id)
            
        
        data = api.order(collection, inputs, products)    
        logger.info(json.dumps(data, indent=4))