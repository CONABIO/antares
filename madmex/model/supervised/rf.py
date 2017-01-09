'''
Created on Nov 25, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.externals import joblib

from madmex.model.base import BaseModel
from madmex.util import create_file_name

class Model(BaseModel):
    '''
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.model = RandomForestClassifier(n_estimators=150,n_jobs=8)
        self.model_name = 'rf'

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
        joblib.dump(self.model, create_file_name(filepath,'%s.pkl' % self.model_name)) 

    def load(self, filepath):
        '''
        Loads an already train model from a file to perform predictions.
        '''
        self.model = joblib.load(create_file_name(filepath,'%s.pkl' % self.model_name))

    def score(self, X, y):
        '''
        Lets the user load a previously trained model to predict with it. 
        '''
        return self.model.score(X,y)
