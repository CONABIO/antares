'''
Created on Jun 25, 2015

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
        parser.add_argument('sum', nargs=2, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--output', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        sum_of_numbers = 0
        from_number = int(options['sum'][0])
        to_number = int(options['sum'][1])
        for number in range(from_number, to_number + 1):
            sum_of_numbers = sum_of_numbers + int(number)
        text_file = open("from_%s_to_%s.txt" % (from_number, to_number), "w")
        text_file.write("%s" % sum_of_numbers)
        text_file.close()
        print (_('The sum of the numbers from %s to %s is: %s') % (
            from_number,
            to_number,
            sum_of_numbers
            )).encode('utf-8')
        print (_('This is a stub for the Change Detection Command.')).encode('utf-8')
