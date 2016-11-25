'''
Created on Nov 25, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.model.base import BaseModel


class Model(BaseModel):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    def fit(self, X, y):
        return BaseModel.fit(self, X, y)


    def predict(self, X):
        return BaseModel.predict(self, X)


    def save(self, filepath):
        return BaseModel.save(self, filepath)


    def load(self, filepath):
        return BaseModel.load(self, filepath)

        