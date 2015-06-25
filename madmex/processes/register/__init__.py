'''
Created on 10/06/2015

@author: erickpalacios
'''
from madmex.processes.base import Processes

class Process(Processes):
    '''
    classdocs
    '''

    def __init__(self, img):
        '''
        Constructor
        '''
        self.name_img = img
    def execute(self):
        '''
        Executer
        '''
    def __str__(self):
        '''
        str
        '''
        return "nombre de sensor a registrar: %s" % (self.name_img)
    