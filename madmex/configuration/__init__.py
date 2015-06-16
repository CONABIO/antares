'''
madmex.configuration

Sets a settings object to be used across the system.
'''

from ConfigParser import MissingSectionHeaderError
import ConfigParser
import importlib
import os
from test.test_socket import try_address

import default_settings
from mhlib import PATH


ENVIRONMENT_VARIABLE = "MADMEX_SETTINGS_MODULE"

def set_settings_from_configuration(settings, parser):
    for section in parser.sections():
        for option in parser.options(section):
            setattr(settings, option.upper(), parser.get(section, option))

class Settings(object):
    def __init__(self):
        self._load()
        
        
    def _load(self):
        settings_file = os.environ.get(ENVIRONMENT_VARIABLE)
        

        path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'configuration.ini'
        )
        
        if settings_file and os.path.isfile(settings_file):
            settings_files = [path, settings_file]
        else:
            settings_files = [path]
        self.SETTINGS_FILES = settings_files
        parser = ConfigParser.SafeConfigParser()
        # TODO: fail gracefully when no header is detected at the beginning
        #of the configuration file. 
        parser.read(settings_files)

        set_settings_from_configuration(self, parser)
        
    def reload(self):
        self._load()

settings = Settings()
