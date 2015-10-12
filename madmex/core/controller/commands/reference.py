'''
Created on Oct 8, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex import _, util
from madmex.core.controller.base import BaseCommand
from madmex.preprocessing.maskingwithreference import create_reference_image


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
        parser.add_argument('--name', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        paths = options['paths']
        name = ''.join(options['name'])
        
        new_paths = map(util.get_parent, paths)
        
        print new_paths
        create_reference_image('/Users/agutierrez/Development/df/new/%s' % name, new_paths, len(new_paths))