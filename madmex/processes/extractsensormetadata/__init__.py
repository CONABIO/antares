
'''
Created on 10/06/2015

@author: erickpalacios
'''

from madmex.processes.base import Processes
from madmex.processes.extractsensormetadata.parser.xmlparser import XmlParser
from madmex.mapper.parser.landsat import LandsatParser
from madmex import load_class

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
        
        if extension_metadata == '.xml':
            sensor_class = load_class(SENSORS_PACKAGE, 'rapideye').Sensor()
            metadata = XmlParser(self.metadata_path, sensor_class.tagList)
            metadata.run(sensor_class.metadata)
            self.output = sensor_class
        else:
            if extension_metadata == '.dim':
                sensor_class = load_class(SENSORS_PACKAGE, 'spot').Sensor()
                metadata = XmlParser(self.metadata_path, sensor_class.tagList)
                metadata.run(sensor_class.metadata)
                self.output = sensor_class
            else:
                if extension_metadata == '.txt':
                    self.output = 'vacio'
                else:
                    print 'no parser'