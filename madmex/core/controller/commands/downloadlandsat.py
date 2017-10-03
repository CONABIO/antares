'''
Created on Oct 3, 2017

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.core.controller.base import BaseCommand
from madmex.util import download_landsat_scene



class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--url', nargs='*', help='This argument represents'
            ' the first image to be processed.')
        parser.add_argument('--name', nargs='*', help='This argument represents'
            ' the first image to be processed.')
        parser.add_argument('--directory', nargs='*', help='This argument represents'
            ' the first image to be processed.')

    def handle(self, **options):
        '''
        This command is used to query the catalog database.
        '''
        url = options['url'][0]
        name = options['name'][0]
        directory = options['directory'][0]
        
        download_landsat_scene(url, directory, name)