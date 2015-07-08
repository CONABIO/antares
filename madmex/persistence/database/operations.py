'''
Created on Jul 7, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

from madmex.persistence.base import BasePersist, BaseAction


LOGGER = logging.getLogger(__name__)

class DatabasePersist(BasePersist):
    def persist(self):
        BasePersist.persist(self)
        
    def get(self, token):
        BasePersist.find_by_id(self, token)
        
    def delete(self, token):
        BasePersist.delete_by_id(self, token)
        
        
class InsertAction(BaseAction):
    '''
    This class implements a BaseAction by inserting into a database using the
    given session. It keeps the object that will be inserted in memory to
    deleted in case this is needed.
    '''
    def __init__(self, orm_object, session):
        '''
        Constructor
        '''
        self.orm_object = orm_object
        self.session = session
        self.success = False
    def do(self):
        '''
        Adds the object own by the instance of this class to the session.
        '''
        LOGGER.debug('Insert object %s into database.' % self.orm_object)
        self.session.add(self.orm_object)
        self.success = True
    def undo(self):
        '''
        Deletes the object own by the given instance of this class from the
        session.
        '''
        LOGGER.debug('Insert object %s into database.' % self.orm_object)
        self.session.delete(self.orm_object)
        self.success = False
