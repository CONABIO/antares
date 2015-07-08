'''
Created on Jul 7, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging
import os
import shutil

from madmex.persistence.base import BasePersist, BaseAction


LOGGER = logging.getLogger(__name__)

class FileSystemPersist(BasePersist):
    def persist(self):
        BasePersist.persist(self)
        
    def find_by_id(self, token):
        BasePersist.find_by_id(self, token)
        
    def delete_by_id(self, token):
        BasePersist.delete_by_id(self, token)
        
        
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
        self.file_to_copy = file_to_copy
        self.destination = destination
        self.success = False
        self.new_file = os.path.join(destination, os.path.basename(file_to_copy))
    def do(self):
        '''
        It copies the file to the target location.
        '''
        try:
            LOGGER.debug('Copy file %s to %s.' % (self.file_to_copy, self.destination))
            shutil.copy(self.file_to_copy, self.destination)
            self.success = True
        except IOError:
            print 'Something went wrong during do action.'
            self.success = False
    def undo(self):
        '''
        Removes de file from the target location.
        '''
        try:
            LOGGER.debug('Delete file %s.' % self.new_file)
            os.remove(self.new_file)
            self.success = False
        except IOError:
            print 'Something went wrong during undo action.'
            self.success = True
