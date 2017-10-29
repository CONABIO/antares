'''
Created on Oct 27, 2017

@author: agutierrez
'''
import json
import logging

from madmex.management.base import AntaresBaseCommand
from madmex.models import LandsatCatalog
from madmex.remote import UsgsApi


scenes = ['LC08_L1GT_032027_20151230_20170224_01_T2',
          'LC08_L1GT_016026_20151230_20170224_01_T2',
          'LC08_L1TP_185027_20151230_20170331_01_T1',
          'LC08_L1TP_130027_20151229_20170331_01_T1',
          'LC08_L1GT_171021_20151228_20170331_01_T2',
          'LC08_L1TP_132044_20151227_20170331_01_T1',
          'LC08_L1TP_166041_20151225_20170331_01_T1',
          'LC08_L1TP_127059_20151224_20170331_01_T1',
          'LC08_L1GT_015026_20151223_20170224_01_T2',
          'LC08_L1TP_136027_20151223_20170331_01_T1',]

logger = logging.getLogger(__name__)

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
        #scenes = LandsatCatalog.objects.filter(row=row, path=path)

        inputs = []
        
        collection = 'olitirs8_collection'
        products = ['sr', 'pixel_qa']
        
        for scene in scenes:
            data = api.get_available_products(scene)
            inputs.append(data[collection]['inputs'][0])
            
        
        data = api.order(collection, inputs, products)
            
        logger.info(json.dumps(data, indent=4))