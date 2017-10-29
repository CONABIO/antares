'''
Created on Oct 27, 2017

@author: agutierrez
'''
import json
import logging

from madmex.management.base import AntaresBaseCommand
from madmex.models import LandsatCatalog
from madmex.remote import UsgsApi, maybe_download_and_extract


logger = logging.getLogger(__name__)

images = ['LC08_L1TP_026047_20171022_20171022_01_RT',
          'LC08_L1TP_026047_20171006_20171023_01_T1',
          'LC08_L1TP_026047_20170920_20171012_01_T1',
          'LC08_L1TP_026047_20170904_20170916_01_T1',
          'LC08_L1TP_026047_20170819_20170826_01_T1']


class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--order', nargs=1)

    def handle(self, *args, **options):
        
        order_id = options['order'][0]
        
        api = UsgsApi()
        
        data = api.get_functions()
        
        row = 26
        path = 47
        
        
        '''
        data = api.get_available_products(images[0])
        products = data['olitirs8_collection']['products']
        data = api.order(images, products)
        '''
        
        order_id = "espa-amaury.gtz@gmail.com-10282017-193609-629"
        
        data = api.get_list_order(order_id)
        #print json.dumps(data, indent=4)
        
        for scene in data[order_id]:
            print scene['product_dload_url']
            maybe_download_and_extract('/Users/agutierrez/Documents/scene026036', scene['product_dload_url'])
        
        #maybe_download_and_extract('/Users/agutierrez/Documents/scene026036', scene['product_dload_url'])
        #data = api._consume_api('/v0')
        #print json.dumps(data, indent=4)
        #data = api.get_available_products('LC08_L1TP_029030_20161008_20170220_01_T1')
        
        
        #data = api.get_user_info()
        
        #api.get_list_order(order_id)
        
        
        #print json.dumps(data, indent=4)
        