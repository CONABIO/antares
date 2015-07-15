'''
Created on Jul 7, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

class BaseAction(object):
    '''
    This class represents an action that can be done and then undone in case
    that such a behavior is needed.
    '''
    def __init__(self):
        '''
        Constructor
        '''
    def act(self):
        '''
        Performs the action that the implementor represents.
        '''
        raise NotImplementedError('Extending class must implement a act method.')
    def undo(self):
        '''
        Undoes the action that the implementor represents.
        '''
        raise NotImplementedError('Extending class must implement a undo method.')
