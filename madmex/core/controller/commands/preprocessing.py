'''
Created on 22/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

import logging
import os

from madmex import find_in_dir, load_class
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands import get_bundle_from_path
from madmex.util import relative_path


LOGGER = logging.getLogger(__name__)
PREPROCESSING_PACKAGE = 'madmex.mapper.bundle'

def _get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    return get_bundle_from_path(path, '../../../mapper', PREPROCESSING_PACKAGE)


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        This command defines only an additional argument. The user must provide
        a path to directory and the name of the folder with the information that will be preprocessed
        '''
        parser.add_argument('--path', nargs='*')
        parser.add_argument('--name', nargs='*')
    def handle(self, **options):
        '''
        This is the code that do preprocessing.
        '''
        path_directory = options['path'][0]
        name = options['name'][0]
        for root, dirs, files in os.walk(path_directory):
            if os.path.basename(root) in dirs:
                dirs.remove(os.path.basename(root))
            if name in dirs:
                path =  os.path.join(root, name)
                bundle = _get_bundle_from_path(path)
                if bundle:
                    LOGGER.info('Directory %s is a %s bundle.', path, bundle.get_name())
                    bundle.preprocess()
                else:
                    LOGGER.info('No bundle was able to identify the directory: %s.', path)

                

