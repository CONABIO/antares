'''
MADMex root package.
'''
from __future__ import unicode_literals

import gettext
from importlib import import_module
import logging
import os
import pkgutil

from madmex.core.log import setup_logging


__version__ = '2.1'
os.environ['LANGUAGE'] = 'es_MX'

LOCALE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'locale')

LANGUAGE = gettext.translation('madmex', LOCALE_PATH)
LANGUAGE.install()
_ = LANGUAGE.ugettext

LOGGER = logging.getLogger(__name__)


def setup():
    '''
    Calls method that sets up the configuration of the logging framework.
    '''
    setup_logging()

def get_version():
    '''
    Returns version for the project.
    '''
    return __version__

def find_in_dir(path, package):
    '''
    Given a path to a directory, returns a list of all the module names
    that are available.

    Returns an empty list if no commands are defined.
    '''
    directory = os.path.join(path, package)
    return [name for _, name, is_pkg in pkgutil.iter_modules([directory])
            if not is_pkg and not name.startswith('_')]

def load_class(package, name):
    '''
    Given a package and a name, it returns an instance of the class that is
    named like that. All errors raised by the import process
    (ImportError, AttributeError) are allowed to propagate.
    '''
    module = import_module('%s.%s' % (package, name))
    return module
