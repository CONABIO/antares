'''
Created on 10/06/2015

@author: erickpalacios
'''

from madmex.processes.base import Processes

class Process(Processes):
    '''
    classdocs
    '''
    def __init__(self, path):
        self.path = path
    def execute(self):
        print self.path