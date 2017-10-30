'''
Created on Oct 27, 2017

@author: agutierrez
'''

import logging

from madmex.management.base import AntaresBaseCommand
from madmex.remote import UsgsApi, maybe_download_and_extract


logger = logging.getLogger(__name__)

class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--directory', nargs=1)
        parser.add_argument('--order', nargs=1)

    def handle(self, *args, **options):
        order_id = options['order'][0]
        directory = options['directory'][0]
        api = UsgsApi()
        data = api.get_list_order(order_id)
        for scene in data[order_id]:
            if scene['status'] == 'complete':
                maybe_download_and_extract(directory, scene['product_dload_url'])
