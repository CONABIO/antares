'''
Created on Oct 27, 2017

@author: agutierrez
'''
import logging

from madmex.management.base import AntaresBaseCommand
from madmex.remote import UsgsApi


logger = logging.getLogger(__name__)

class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--order', nargs=1)

    def handle(self, *args, **options):
        
        order_id = options['order'][0]
        
        api = UsgsApi()
        api.list_order(order_id)