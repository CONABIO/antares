'''
Created on Jul 7, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging
import os
import shutil

from madmex.persistence.base import BaseAction


LOGGER = logging.getLogger(__name__)

class InsertAction(BaseAction):
    '''
    This implementation of the BaseAction class represents a file copy. When
    the action is executed, the file is copied to the desired destination. If
    the action needs to be undone, the file is removed from the target location.
    '''
    def __init__(self, file_to_copy, destination):
        '''
        Constructor
        '''
        super(InsertAction,self).__init__()
        self.file_to_copy = file_to_copy
        self.destination = destination
        self.success = False
        self.new_file = os.path.join(destination, os.path.basename(file_to_copy))
    def act(self):
        '''
        It copies the file to the target location.
        '''
        try:
            LOGGER.debug('Copy file %s to %s.', self.file_to_copy, self.destination)
            shutil.copy(self.file_to_copy, self.destination)
            self.success = True
        except IOError:
            LOGGER.debug('Something went wrong during act action, probably the'
                'file %s does not exists.' % self.file_to_copy)
            self.success = False
    def undo(self):
        '''
        Removes the file from the target location.
        '''
        try:
            LOGGER.debug('Delete file %s.', self.new_file)
            if self.success:
                os.remove(self.new_file)
                self.success = False
        except IOError:
            LOGGER.debug('Something went wrong during undo action.')
            self.success = True
