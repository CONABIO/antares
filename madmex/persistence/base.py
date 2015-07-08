'''
Created on Jul 7, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

class BasePersist():
    def __init__(self):
        '''
        Constructor
        '''
    def persist(self):
        '''
        '''
        raise NotImplemented(
                             'Extending classes must provide a way to persist.'
                             'objects.'
                             )
    def find_by_id(self, token):
        '''
        The implementors of this method should retrieve the object that had been
        persisted in the past using the id.
        '''
        raise NotImplemented(
                            'Extending classes must provide a way to find'
                            'objects using its id.'
                            )
    def delete_by_id(self, token):
        '''
        Implementors of this method should perform the necessary process to
        delete an object that had been persisted in the past using the id.
        '''
        raise NotImplemented(
                            'Extending classes must provide a way to delete'
                            'objects using its id.'
                            )
        
class BaseAction():
    '''
    This class represents an action that can be done and then undone in case
    that such a behavior is needed.
    '''
    def __init__(self):
        '''
        Constructor
        '''
    def do(self):
        '''
        Performs the action that the implementor represents.
        '''
        raise NotImplemented('Extending class must implement a do method.')
    def undo(self):
        '''
        Undoes the action that the implementor represents.
        '''
        raise NotImplemented('Extending class must implement a undo method.')