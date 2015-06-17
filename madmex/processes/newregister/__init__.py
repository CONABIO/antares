'''
Created on 10/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals
from madmex.processes.base import Processes

class Command(Processes):
    '''
    classdocs
    '''

    def __init__(self, name):
        '''
        Constructor
        '''
        self.name_sensor = name
    def execute(self):
        '''
        Executer
        '''
    def __str__(self):
        '''
        str
        '''
        return "nombre de sensor a registrar: %s" % (self.name_sensor)
    