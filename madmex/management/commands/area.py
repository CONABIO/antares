'''
Created on Oct 31, 2017

@author: agutierrez
'''

from __future__ import unicode_literals

import logging

from madmex.management.base import AntaresBaseCommand


logger = logging.getLogger(__name__)

class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--path', nargs=1, help='Path to image.')

    def handle(self, **options):
        
        filepath = options['path'][0]
        print filepath