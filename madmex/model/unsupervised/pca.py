'''
Created on Dec 2, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

from sklearn.decomposition.pca import PCA
from sklearn.externals import joblib

from madmex.util import create_file_name


class Model(object):
    '''
    classdocs
    '''


    def __init__(self, n_components):
        '''
        Constructor
        '''
        self.model = PCA(n_components=5)
        self.model_name = 'pca'
        
    def fit(self, X):
        '''
        Performs a principal component analysis.
        '''
        self.model.fit(X)
        
        variance = self.model.explained_variance_ratio_
        print variance
        
    def transform(self, X):
        '''
        Transforms the given data with the eigenvalues found in the principal
        component analysis.
        '''
        return self.model.transform(X)
        
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