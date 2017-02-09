'''
Created on Feb 9, 2017

@author: rmartinez
'''
from __future__ import unicode_literals

from sklearn import svm
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
        self.model = svm(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
                         decision_function_shape='ovo', degree=3, gamma='auto', kernel='rbf',
                         max_iter=-1, probability=False, random_state=None, shrinking=True,
                         tol=0.001, verbose=False)
        
        self.model_name = 'svm'

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
