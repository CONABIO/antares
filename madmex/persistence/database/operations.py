'''
Created on Jul 7, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

from sqlalchemy.exc import IntegrityError

from madmex.persistence.base import BaseAction


LOGGER = logging.getLogger(__name__)
        
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
    def act(self):
        '''
        Adds the object own by the instance of this class to the session.
        '''
        LOGGER.debug('Insert object %s into database.' % self.orm_object)
        try:
            self.session.add(self.orm_object)
            self.session.commit()
            self.success = True
        except IntegrityError:
            LOGGER.debug('Duplicate key value violates unique constraint.')
            self.success = False
        except Exception:
            LOGGER.debug('Error during database insertion.')
            self.success = False
    def undo(self):
        '''
        Deletes the object own by the given instance of this class from the
        session.
        '''
        if self.success:
            LOGGER.debug('Delete object %s from database.' % self.orm_object)
            self.session.delete(self.orm_object)
            self.session.commit()
        self.success = False
