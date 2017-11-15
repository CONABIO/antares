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
        parser.add_argument('--sensor', nargs=1)

    def handle(self, *args, **options):
        row = options['row'][0]
        path = options['path'][0]
        sensor = options['sensor'][0]
        api = UsgsApi()
        scenes = LandsatCatalog.objects.filter(row=row, path=path, sensor=sensor)[:10]

        inputs = []
        
        collection = OLI_TIRS
        products = ['sr', 'pixel_qa']
        

        for scene in scenes:
            print scene.landsat_product_id
            if scene.landsat_product_id != 'LC08_L1TP_026047_20160222_20170224_01_T1':
                inputs.append(scene.landsat_product_id)
            
        
        data = api.order(collection, inputs, products)    
        logger.info(json.dumps(data, indent=4))