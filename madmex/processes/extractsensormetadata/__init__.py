
'''
Created on 10/06/2015

@author: erickpalacios
'''

from madmex.processes.base import Processes
from madmex import load_class
from madmex.mapper.sensor import get_sensors_and_metadata_extensions

SENSORS_PACKAGE = 'madmex.mapper.sensor'

class Process(Processes):
    '''
    classdocs
    '''
    def __init__(self, diction):
        self.diction = diction
        self.metadatapath = self.diction['metadata']         
    def execute(self):
        extensionmetadata = self.get_extension(self.metadatapath).strip('.')
        sensorsmetadataext = get_sensors_and_metadata_extensions()
        if extensionmetadata in sensorsmetadataext.keys():
            sensorclass = load_class(SENSORS_PACKAGE, sensorsmetadataext[extensionmetadata]).Sensor()
        sensorclass.extract_metadata(self.metadatapath)
        self.output = sensorclass