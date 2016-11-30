'''
Created on Nov 25, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.externals import joblib

from madmex.model.base import BaseModel

class Model(BaseModel):
    '''
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.model = RandomForestClassifier(n_estimators=200,n_jobs=20)
    def fit(self, X, y):
        self.model.fit(X,y)

    def predict(self, X):
        '''
        Simply passes down the prediction from the underlying model.
        '''
        return self.model.predict(X)

    def save(self, filepath):
        '''
        Persists the trained model to a file.
        '''
        joblib.dump(self.model, filepath) 

    def load(self, filepath):
        '''
        Loads an already train model from a file to perform predictions.
        '''
        self.model = joblib.load(filepath)
    def score(self, X, y):
        '''
        Lets the user load a previously trained model to predict with it. 
        '''
        return self.model.score(X,y)
