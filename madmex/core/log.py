'''
Created on Jun 15, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging
import logging.config
import sys

from madmex.configuration import SETTINGS


LOGGER = logging.getLogger(__name__)

def setup_logging():
    '''
    This method sets the log level of the logging framework using the value
    found in SETTINGS. If the value found does not exist in the log level
    catalog, the program finishes with 0 signal.
    '''
    try:
        logging.config.dictConfig(get_configuration_dict(getattr(SETTINGS, 'LOG_LEVEL')))
    except ValueError:
        LOGGER.error('Log level %s does not exist, please fix your'
                     ' configuration file.' % getattr(SETTINGS, 'LOG_LEVEL'))
        sys.exit(0)
    LOGGER.info('Log level is now set to %s.' % getattr(SETTINGS, 'LOG_LEVEL'))

def get_configuration_dict(log_level):
    '''
    Returns a dictionary containing the default SETTINGS for the logging
    framework. Log level value is set to the given log leve.
    '''
    configuration_dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '[%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '[%(levelname)s] %(asctime)s  %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': log_level,
                'class':'logging.StreamHandler',
                'formatter': 'standard',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': log_level,
                'propagate': True
            },
        }
    }
    return configuration_dict
