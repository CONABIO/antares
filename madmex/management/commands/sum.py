'''
Created on Jun 25, 2015

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
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('sum', nargs='+', help='Just sum the numbers in the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        sum_of_numbers = 0
        for number in options['sum']:
            sum_of_numbers = sum_of_numbers + int(number)
        
        logger.info('The sum of the numbers is: %s' % sum_of_numbers)
