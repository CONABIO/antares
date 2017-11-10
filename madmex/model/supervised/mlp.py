'''
Created on Feb 2, 2017

@author: rmartinez
'''
from __future__ import unicode_literals

from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
from madmex.model.base import BaseModel
from madmex.util import create_filename



class Model(BaseModel):
    '''
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.model = MLPClassifier(solver='lbfgs', max_iter=600, hidden_layer_sizes=(300,), random_state=1)
        #self.model = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(200,7), random_state=1)
        #self.model = MLPClassifier(activation='relu', alpha=1e-05, batch_size='auto',
        #                           beta_1=0.9, beta_2=0.999, early_stopping=False,
        #                           epsilon=1e-08, hidden_layer_sizes=(200,), learning_rate='constant',
        #                           learning_rate_init=0.001, max_iter=300, momentum=0.9,
        #                           nesterovs_momentum=True, power_t=0.5, random_state=1, shuffle=True,
        #                           solver='lbfgs', tol=0.0001, validation_fraction=0.1, verbose=False,
        #                           warm_start=False)
        
        self.model_name = 'mlp'
        self.scaler_mlp = 'scaler'
        self.scaler = StandardScaler()
        
        
    def fit(self, X, y):
        self.scaler.fit(X)
        X_train = self.scaler.transform(X)
        self.model.fit(X_train,y)

    def predict(self, X):
        '''
        Simply passes down the prediction from the underlying model.
        '''
        X_train = self.scaler.transform(X)
        return self.model.predict(X_train)

    def save(self, filepath):
        '''
        Persists the trained model to a file.
        '''
        joblib.dump(self.model, create_filename(filepath,'%s.pkl' % self.model_name)) 
        joblib.dump(self.scaler, create_filename(filepath,'%s.pkl' % self.scaler_mlp)) 


    def load(self, filepath):
        '''
        Loads an already train model from a file to perform predictions.
        '''
        self.model = joblib.load(create_filename(filepath,'%s.pkl' % self.model_name))
        self.scaler = joblib.load(create_filename(filepath,'%s.pkl' % self.scaler_mlp))


    def score(self, X, y):
        '''
        Lets the user load a previously trained model to predict with it. 
        '''
        return self.model.score(X,y)

    
