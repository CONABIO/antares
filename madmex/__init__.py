'''
MADMex root package.
'''
import os
import pkgutil
from importlib import import_module

__version__ = "2.1"

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