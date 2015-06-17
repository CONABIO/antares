'''
Created on 10/06/2015

@author: erickpalacios
'''

from importlib import import_module
from madmex import load_class
from madmex.processes.base import Processes

PROCESSES_PACKAGE = 'madmex.processes'      
class Manager(object):
    '''
    Manager
    '''
    def __init__(self, process):
        self.process = process
    def execute(self):
        '''
        Execute
        '''
        print self.load_processes_class(PROCESSES_PACKAGE)
        #lo que sigue:
        #instance_class=self.load_processes_class(PROCESSES_PACKAGE)
        #instance_class.execute()
    def load_processes_class(self, package):
        '''
        load_processes_class
        '''
        module = load_class(package, self.process.keys()[0])
        #return module.Command(self.process.values()[0][0])
        return module.Command(self.process.get(self.process.keys()[0])[0:])
 