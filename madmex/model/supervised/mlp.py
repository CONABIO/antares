'''
Created on Feb 2, 2017

@author: rmartinez
'''
from __future__ import unicode_literals

from sklearn.neural_network import MLPClassifier
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
        self.model = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
        
        self.model_name = 'mpl'

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

    
