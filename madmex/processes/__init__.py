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
    def __init__(self, process, input_data):
        self.name_process = process
        self.input_data = input_data
    def execute(self):
        '''
        Execute
        '''
        instance_class = self.load_processes_class(PROCESSES_PACKAGE)
        instance_class.execute()
        self.output_data = instance_class.output
    def execute_parallel(self):
        '''
        execute in parallel some process
        receives a directory with folders within. Instance Process() for each folder separately
        '''
    def load_processes_class(self, package):
        '''
        load_processes_class
        '''
        module = load_class(package, self.name_process)
        return module.Process(self.input_data)
 