'''
Created on Jun 3, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex import _
from madmex.core.controller.base import BaseCommand


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('sum', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        sum_of_numbers = 0
        for number in options['sum']:
            sum_of_numbers = sum_of_numbers + int(number)
        print (_('The sum of the numbers is: %s') % sum_of_numbers).encode('utf-8')
        print (_('This is a stub for the Change Detection Command.')).encode('utf-8')
