'''
madmex.configuration

Sets a SETTINGS object to be used across the system.
'''
from __future__ import unicode_literals

from ConfigParser import MissingSectionHeaderError
import ConfigParser
import importlib
import logging
import os
from os.path import join, dirname

from dotenv.main import load_dotenv


ENVIRONMENT_VARIABLE = "MADMEX_SETTINGS_MODULE"
LOGGER = logging.getLogger(__name__)

def set_settings_from_configuration(settings, parser):
    '''
    Reads a configuration file, it traverses the sections taking the (key,value)
    pairs and setting them as the SETTINGS object attributes.
    '''
    for section in parser.sections():
        for option in parser.options(section):
            setattr(settings, option.upper(), parser.get(section, option))
def set_settings_from_environment(settings, variables):
    '''
    Reads sensitive information from the environment so passwords are not uploaded into
    the repository.
    '''
    for variable in variables:
        setattr(settings, variable.upper(), os.environ.get(variable.upper()))
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
        self.load()
    def load(self):
        '''
        Protected method to read the file for the first time.
        '''
        settings_file = os.environ.get(ENVIRONMENT_VARIABLE)
        path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'configuration.ini')
        if settings_file and os.path.isfile(settings_file):
            settings_files = [path, settings_file]
        else:
            settings_files = [path]
        setattr(self, 'SETTINGS_FILES', settings_files)
        parser = ConfigParser.SafeConfigParser()
        # TODO: fail gracefully when no header is detected at the beginning.
        parser.read(settings_files)

        set_settings_from_configuration(self, parser)
        
        dotenv_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '.env')

        if os.path.isfile(dotenv_path):
            load_dotenv(dotenv_path)
            set_settings_from_environment(self, getattr(self, 'ENVIRON').split(','))
        else:
            LOGGER.warning('There is no .env file in the configuration folder.')
    def reload(self):
        '''
        This public method will call the load method when a new file has been
        configured. This only exists for semantic reasons.
        '''
        self.load()

SETTINGS = Settings()
