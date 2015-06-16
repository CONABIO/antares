'''
MADMex root package.
'''
from __future__ import unicode_literals

import gettext
from importlib import import_module
import locale
import logging
import os
import pkgutil

from madmex.core.log import setup_logging


__version__ = '2.1'
os.environ['LANGUAGE'] = 'es_MX'

locale_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'locale'
        )

print locale_path

language = gettext.translation ('madmex', locale_path)
language.install()
_ = language.ugettext

logger = logging.getLogger(__name__)


def setup():
    setup_logging()

def get_version():
    '''
    Returns version for the project.
    '''
    return __version__

def find_in_dir(path, package):
    directory = os.path.join(path, package)
    return [name for _, name, is_pkg in pkgutil.iter_modules([directory])
            if not is_pkg and not name.startswith('_')]
    
def load_class(package,name):
    module = import_module('%s.%s' % (package, name))
    return module