'''
Created on 29/06/2015

@author: erickpalacios
'''
from madmex.mapper.base import BaseSensor
from datetime import datetime
import madmex.mapper.parser.rapideye as rapideyeparser


class Sensor(BaseSensor):
    '''
    classdocs
    '''
    def __init__(self):
        self.sensor_name = 'spot'
        self.metadata_ext = 'dim'
        self.metadata = {
                    "productname" : "PROCESSING_LEVEL",
                    "sensor" : "MISSION",
                    "platform" : "MISSION_INDEX",
                    "dateCreation" : "DATASET_PRODUCTION_DATE",
                    "dataAcquisition" : "IMAGING_DATE",
                    "dataAcquisitionTime" : "IMAGING_TIME",
                    "angle": "VIEWING_ANGLE",
                    "tileid" : "GRID_REFERENCE"
                    }

            
    def extract_metadata(self, metadata_path):
        instance_class = rapideyeparser.Parser(metadata_path, self.metadata)
        instance_class.parse()
        self.metadata = instance_class.metadata
        acquisitionDate = self.metadata["dataAcquisition"]
        acquisitionTime = self.metadata["dataAcquisitionTime"]
        creationDate = self.metadata["dateCreation"]
        self.metadata["dataAcquisition"] = datetime.strptime(acquisitionDate+"T"+acquisitionTime, "%Y-%m-%dT%H:%M:%S")
        self.metadata["dateCreation"] = datetime.strptime(creationDate, "%Y-%m-%dT%H:%M:%S.%f")
        self.metadata["clouds"] = 999
        self.metadata["angle"] = float(self.metadata["angle"])  
        self.metadata["quicklook"] = "PREVIEW.JPG"

        
    