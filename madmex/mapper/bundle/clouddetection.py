'''
Created on Mar 9, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

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
        parser.add_argument('--paths', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        paths = options['paths']
        print paths
        tiles = options['tiles']
        name = ''.join(options['name'])

        from madmex.mapper.bundle.rapideye import Bundle
        
        
        if paths:
            pass
