'''
Created on Nov 24, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import abc


class BaseModel(object):
    '''
    This class works as a wrapper to have a single interface to several
    models and machine learning packages. This will hide the complexity
    of the different ways in which the algorithms are used.
    '''
    __metaclass__ = abc.ABCMeta
    def __init__(self, params):
        '''
        Constructor
        '''
    def fit(self, X, y):
        '''
        This method will train the classifier with given data.
        '''
        raise NotImplementedError('subclasses of BaseBundle must provide a fit() method')
    def predict(self, X):
        '''
        When the model is created, this method lets the user predict on unseen data.
        '''
        raise NotImplementedError('subclasses of BaseBundle must provide a predict() method')
    def save(self, filepath):
        '''
        This method lets the user persist a trained model to disc.
        '''
        raise NotImplementedError('subclasses of BaseBundle must provide a save() method')
    def load(self, filepath):
        '''
        Lets the user load a previously trained model to predict with it. 
        '''
        raise NotImplementedError('subclasses of BaseBundle must provide a load() method')
        