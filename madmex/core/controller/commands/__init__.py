'''
mamdex.core.constroller.commands
Commands package.
'''
from __future__ import unicode_literals

import logging

from madmex import find_in_dir, load_class
from madmex.util import relative_path, get_last_package_from_name


LOGGER = logging.getLogger(__name__)

def load_bundle(name, path, package):
    '''
    Loads the python module with the given name found in the path.
    '''
    module = load_class(package, name)
    return module.Bundle(path)


def get_bundle_from_path(path, bundle_directory, package):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    LOGGER.debug('Path: %s will be processed.', path)
    bundles = find_in_dir(relative_path(__file__, bundle_directory), get_last_package_from_name(package))
    for bundle_name in bundles:
        bundle = load_bundle(bundle_name, path, package)
        if bundle.can_identify():
            return bundle
        else:
            LOGGER.info('Directory %s is not a %s bundle.', path, bundle.get_name())
    return None
