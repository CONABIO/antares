'''
Created on 22/07/2015

@author: erickpalacios
'''


import logging

from madmex import find_in_dir, load_class
from madmex.core.controller.base import BaseCommand
from madmex.util import relative_path
import os

LOGGER = logging.getLogger(__name__)
PREPROCESSING_PACKAGE = 'madmex.preprocessing.sensor'

def load_bundle(name, path):
    '''
    Loads the python module with the given name found in the path.
    '''
    module = load_class(PREPROCESSING_PACKAGE, name)
    return module.Bundle(path)

def get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    LOGGER.debug('Path: %s will be processed.', path)
    bundles = find_in_dir(relative_path(__file__, '../../../preprocessing'), 'sensor')
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
        a path to preprocessed and the name of the folder with the information
        '''
        parser.add_argument('--path', nargs='*')
        parser.add_argument('--name', nargs='*')
    def handle(self, **options):
        '''
        This is the code that does preprocessing.
        '''
        path_directory = options['path'][0]
        name = options['name'][0]
        for root, dirs, files in os.walk(path_directory):
            if name in dirs:
                path =  os.path.join(root, name)
                bundle = get_bundle_from_path(path)
                if bundle:
                    LOGGER.info('Directory %s is a %s bundle.', path, bundle.get_name())
                    bundle.preprocessing()
                else:
                    LOGGER.info('No bundle was able to identify the directory: %s.', path)
