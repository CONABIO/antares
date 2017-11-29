'''
Created on Nov 29, 2017

@author: agutierrez
'''
import logging

from madmex.management.base import AntaresBaseCommand


logger = logging.getLogger(__name__)

class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--path', nargs='1', help='The file to be segmented.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        logger.info('Segmentation example.')