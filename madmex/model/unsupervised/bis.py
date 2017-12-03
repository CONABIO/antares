'''
Created on Dec 2, 2017

@author: agutierrez
'''
from madmex.model.base import BaseModel

OPTIONS = {'t':50,
           's':0.7,
           'c':0.3,
           'mp':True,
           'xt':40,
           'rows':625
          }

class Model(BaseModel):
    '''
    classdocs
    '''


    def __init__(self, options=None):
        '''
        Constructor
        '''
        if not options:
            self.t = OPTIONS['t']
            self.s = OPTIONS['s']
            self.c = OPTIONS['c']
            self.mp = OPTIONS['mp']
            self.xt = OPTIONS['xt']
            self.rows = OPTIONS['rows']
    
    def predict(self, X):
        pass