
'''
Created on 10/06/2015

@author: erickpalacios
'''

from madmex.processes.base import Processes
from madmex import load_class
from madmex.mapper.sensor import get_sensor_and_metadata_extensions

SENSORS_PACKAGE = 'madmex.mapper.sensor'

class Process(Processes):
    '''
    classdocs
    '''
    def __init__(self, diction):
        self.diction = diction
        self.metadata_path = self.diction['metadata']         
    def execute(self):
        extension_metadata = self.get_extension(self.metadata_path).strip('.')
        sensors_metadata_ext = get_sensor_and_metadata_extensions()
        if extension_metadata in sensors_metadata_ext.keys():
            sensor_class = load_class(SENSORS_PACKAGE, sensors_metadata_ext[extension_metadata]).Sensor()
        metadata = sensor_class.parser(self.metadata_path)
        metadata.parse()
        sensor_class.metadata = metadata.metadata
        sensor_class.change_format()            
        self.output = sensor_class