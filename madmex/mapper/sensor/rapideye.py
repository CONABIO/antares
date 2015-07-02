'''
Created on 29/06/2015

@author: erickpalacios
'''
from datetime import datetime

from madmex.mapper.base import BaseSensor
import madmex.mapper.parser.rapideye as rapideyeparser



class Sensor(BaseSensor):
    '''
    classdocs
    '''
    def __init__(self):
        self.sensor_name = 'rapideye'
        self.metadata_ext = 'xml'
        self.metadata = {
                    "productname" : "eop:productType",
                    "sensor" : "eop:sensorType",
                    "platform" : "eop:serialIdentifier",
                    "dataAcquisition" : "eop:acquisitionDate",
                    "dateCreation" : "eop:archivingDate",
                    "clouds": "opt:cloudCoverPercentage",
                    "angle": "eop:incidenceAngle",
                    "azimuthAngle": "re:azimuthAngle",
                    "solarazimuth": "opt:illuminationAzimuthAngle",
                    "solarzenith": "opt:illuminationElevationAngle",
                    "quicklook" : "eop:fileName",
                    "tileid" : "re:tileId"
                    }
        self.metadata_path = None
    def extract_metadata(self, metadata_path):
        instance_class = rapideyeparser.Parser(metadata_path, self.metadata)
        instance_class.parse()
        self.metadata = instance_class.metadata
        acquisitionDate = self.metadata["dataAcquisition"]
        creationDate = self.metadata["dateCreation"] 
        self.metadata["dataAcquisition"] = datetime.strptime(acquisitionDate, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.metadata["dateCreation"] = datetime.strptime(creationDate, "%Y-%m-%dT%H:%M:%SZ")   
        self.metadata["clouds"] = float(self.metadata["clouds"])    
        self.metadata["angle"] = float(self.metadata["angle"])
      
        

            