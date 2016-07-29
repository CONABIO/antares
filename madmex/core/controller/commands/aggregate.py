'''
Created on Jul 29, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        This command defines only an additional argument. The user must provide
        a path to ingest, if several paths are given, all of the folders will
        be ingested.
        '''
        parser.add_argument('--path', nargs='*')
    def handle(self, **options):
        
        path = options['path'][0]
        
        data_array = open_handle(path)
        
        
        
        print data_array.shape
        
        print path
        