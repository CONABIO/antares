'''
madmex.configuration

Sets a SETTINGS object to be used across the system.
'''
from __future__ import unicode_literals

from ConfigParser import MissingSectionHeaderError
import ConfigParser
import importlib
import os

ENVIRONMENT_VARIABLE = "MADMEX_SETTINGS_MODULE"

def set_settings_from_configuration(SETTINGS, parser):
    for section in parser.sections():
        for option in parser.options(section):
            setattr(SETTINGS, option.upper(), parser.get(section, option))

class Settings(object):
    '''
    An instance of this class will read a configuration file and will create
    an attribute with each (key, value) pair found in the file. Values can be
    later overriden if a newer file is loaded. 
    '''
    def __init__(self):
        '''
        constructor
        '''
        self._load()
        
    def _load(self):
        '''
        Protected method to read the file for the first time.
        '''
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
        '''
        This public method will call the load method when a new file has been
        configured. This only exists for semantic reasons.
        '''
        self._load()

SETTINGS = Settings()
