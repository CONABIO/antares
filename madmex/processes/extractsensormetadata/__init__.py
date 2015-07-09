
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
        self.metadata_path = self.diction['metadata']    
    def execute(self):
        extension_metadata = self.get_extension(self.metadata_path)
        sensors_metadata_ext = get_sensors_and_metadata_extensions()
        if extension_metadata in sensors_metadata_ext.keys():
            sensor_module = load_class(SENSORS_PACKAGE, sensors_metadata_ext[extension_metadata])
            sensor_class = sensor_module.Sensor(self.metadata_path)
        self.output = sensor_class