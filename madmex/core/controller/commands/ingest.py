'''
Created on Jul 10, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

from madmex import find_in_dir, load_class
from madmex.core.controller.base import BaseCommand
from madmex.persistence.driver import persist_bundle
from madmex.util import relative_path


LOGGER = logging.getLogger(__name__)
BUNDLE_PACKAGE = 'madmex.mapper.bundle'

def load_bundle(name, path):
    '''
    Loads the python module with the given name found in the path.
    '''
    module = load_class(BUNDLE_PACKAGE, name)
    return module.Bundle(path)

def get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    LOGGER.debug('Path: %s will be processed.', path)
    bundles = find_in_dir(relative_path(__file__, '../../../mapper'), 'bundle')
    for bundle_name in bundles:
        bundle = load_bundle(bundle_name, path)
        if bundle.can_identify():
            return bundle
        else:
            LOGGER.info('Directory %s is not a %s bundle.', path, bundle.get_name())
    return None

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
        '''
        This is the code that does the ingestion.
        '''
        for path in options['path']:
            bundle = get_bundle_from_path(path)
            if bundle:
                LOGGER.info('Directory %s is a %s bundle.', path, bundle.get_name())
                persist_bundle(bundle)
            else:
                LOGGER.info('No bundle was able to identify the directory: %s.', path)
            
                