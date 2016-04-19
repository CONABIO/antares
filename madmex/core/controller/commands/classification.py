'''
Created on Apr 19, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

from madmex.core.controller.base import BaseCommand

LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--satellite', nargs='*', help='The type of satellite \
            that generated the images for this process, right now this supports \
            rapideye and landsat.')

    def handle(self, **options):
        '''
        Constructor
        '''
        shape_name = options['satellite'][0]
        
        LOGGER.info('The %s classification process will be started.' % shape_name)

        