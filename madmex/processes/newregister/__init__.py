'''
Created on 10/06/2015

@author: erickpalacios
'''
from madmex.processes.base import Processes

class Command(Processes):
    '''
    classdocs
    '''


    def __init__(self, name):
        '''
        Constructor
        '''
        self.name_sensor=name
        
    def execute(self):
        '''executer'''
        #vía sqlalchemy se hace el registro en la tabla de sensores y se jala el key correspondiente
            
    def __str__(self):
        
        return "nombre de sensor a registrar: %s" % (self.name_sensor)
    
    
    