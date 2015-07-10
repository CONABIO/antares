'''
Created on Jul 8, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

from madmex.configuration import SETTINGS
from madmex.persistence.database.connection import SESSION_MAKER
import madmex.persistence.database.operations as database
import madmex.persistence.filesystem.operations as filesystem


LOGGER = logging.getLogger(__name__)

def persist_bundle(bundle):
    '''
    This function persist a bundle in both the database and the file system. It
    is responsibility of the bundle to provide information about which files
    should be persisted in the file system, and to build the database object
    that will be inserted in the database. The database is configured using the
    session maker in the connection module. 
    
    In order to achieve its purpose, this method creates a list of the actions
    to perform. Once the list is fully populated, it calls the do method for
    each element in the list. If any of the actions in the list fails, a
    rollback is performed in all of them, the result is the same state as before
    the method was called.
    '''
    destination = getattr(SETTINGS, 'TEST_FOLDER')
    actions = []
    session = SESSION_MAKER()
    try:
        for file_name in bundle.get_files():
            actions.append(filesystem.InsertAction(file_name, destination))
        actions.append(database.InsertAction(
            bundle.get_database_object(), 
            session)
            )

        def do_result(action):
            action.do()
            session.commit()
            return action.success    
        if not reduce(lambda x,y: x and y, map(do_result, actions)):
            LOGGER.debug('Some action went wrong at persistence process, ' 
                'rollback will be performed.')
            print 'Some action went wrong at persistence process, rollback will be performed.'
            for action in actions:
                action.undo()
            session.commit()
        else:
            print 'Ingestion was successful.'
            LOGGER.debug('Ingestion was successful.')
    except Exception:
        print 'Not expected error at persistence.driver'
        LOGGER.error('Not expected error at persistence.driver')
        raise
    finally:
        session.close()
