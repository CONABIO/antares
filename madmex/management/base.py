'''
Created on Oct 27, 2017

@author: agutierrez
'''
import logging
import time

from django.core.management.base import BaseCommand


LOGGER = logging.getLogger(__name__)


class AntaresBaseCommand(BaseCommand):
    '''
    This class just pretends to be a decorator from django base command to provide feedback
    on how much time does a commandt takes to finish.
    '''

    def execute(self, *args, **options):
        '''
        Just wrapping a timer around regular execution.
        '''
        LOGGER.debug('Command line arguments: %s' % options)
        print 'Command line arguments: %s' % options
        start_time = time.time()
        output = BaseCommand.execute(self, *args, **options)
        LOGGER.info('Command execution is done in %s seconds.' % (time.time() - start_time))
        print 'Command execution is done in %s seconds.' % (time.time() - start_time)
        return output

    
    