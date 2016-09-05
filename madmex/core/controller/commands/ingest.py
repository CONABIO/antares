'''
Created on Jul 10, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands import get_bundle_from_path
from madmex.persistence.driver import persist_bundle


LOGGER = logging.getLogger(__name__)
BUNDLE_PACKAGE = 'madmex.mapper.bundle'

def _get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    return get_bundle_from_path(path, '../../../mapper', BUNDLE_PACKAGE)

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
        parser.add_argument('--keep', action='store_true')
    def handle(self, **options):
        '''
        This is the code that does the ingestion.
        '''
        keep = options['keep']
        
        for path in options['path']:
            bundle = _get_bundle_from_path(path)
            if bundle:
                LOGGER.info('Directory %s is a %s bundle.', path, bundle.get_name())
                persist_bundle(bundle, keep)
                
            else:
                LOGGER.info('No bundle was able to identify the directory: %s.', path)
