'''
Created on Jun 15, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging
import logging.config
import sys

from madmex.configuration import settings


logger = logging.getLogger(__name__)

def setup_logging():
    try:
        logging.config.dictConfig(get_configuration_dict(settings.LOG_LEVEL))
    except ValueError:
        logger.error('Log level %s does not exist, please fix your'
                     ' configuration file.' % settings.LOG_LEVEL)
        sys.exit(0)
    logger.info('Log level is now set to %s.' % settings.LOG_LEVEL)
    
def get_configuration_dict(log_level):
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
