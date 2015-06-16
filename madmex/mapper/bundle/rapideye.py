'''
Created on Jun 10, 2015

@author: agutierrez
'''
from madmex.mapper.base import BaseBundle, METADATA, IMAGE, FILE


class Bundle(BaseBundle):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        super(Bundle, self).__init__(params)
        
        
    def is_consistent(self):
        print "help"
        if ((len(self.getFiles(METADATA)) > 0) and 
            (len(self.getFiles(IMAGE)) > 0 ) and 
            (len(self.getFiles(FILE)) > 0)):
            return True
        else:
            return False