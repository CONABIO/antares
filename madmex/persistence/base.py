'''
Created on Jul 7, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

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