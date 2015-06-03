'''
Created on Jun 3, 2015

@author: agutierrez
'''

from madmex.core.controller.base import BaseCommand

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('sum', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, *args, **options):
        sum_of_numbers = 0
        for number in options['sum']:
            sum_of_numbers =  sum_of_numbers + int(number)
        print "The sum of the numbers is: %s" % sum_of_numbers    
        print "This is a stub for the Change Detection Command."