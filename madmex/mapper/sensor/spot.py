'''
Created on 29/06/2015

@author: erickpalacios
'''
from madmex.mapper.base import BaseSensor
from datetime import datetime
import madmex.mapper.parser.xmlparser as xmlparser


class Sensor(BaseSensor):
    '''
    classdocs
    '''
    def __init__(self):
        self.sensor_name = 'spot'
        self.metadata_ext ='dim'
        self.tagList = {
                    "product" : ["Dimap_Document","Data_Processing","PROCESSING_LEVEL"],
                    "sensor" : ["Dimap_Document","Dataset_Sources","Scene_Source","MISSION"],
                    "platform" : ["Dimap_Document","Dataset_Sources","Scene_Source","MISSION_INDEX"],
                    "dateCreation" : ["Dimap_Document","Production","DATASET_PRODUCTION_DATE"],
                    "dataAcquisition" : ["Dimap_Document","Dataset_Sources","Scene_Source","IMAGING_DATE"],
                    "dataAcquisitionTime" : ["Dimap_Document","Dataset_Sources","Scene_Source","IMAGING_TIME"],
                    "angle": ["Dimap_Document","Dataset_Sources","Scene_Source","VIEWING_ANGLE"],
                    "tileid" : ["Dimap_Document","Dataset_Sources","Scene_Source","GRID_REFERENCE"]
                    }
        self.metadata=dict()        

            
    def extract_metadata(self, metadata_path):
        instance_class = xmlparser.Parser(metadata_path, self.tagList)
        instance_class.parse()
        self.metadata = instance_class.metadata           
        acquisitionDate = self.metadata["dataAcquisition"]
        acquisitionTime = self.metadata["dataAcquisitionTime"]
        creationDate = self.metadata["dateCreation"]
        self.metadata["dataAcquisition"] = datetime.strptime(acquisitionDate+"T"+acquisitionTime, "%Y-%m-%dT%H:%M:%S")
        self.metadata["dateCreation"] = datetime.strptime(creationDate, "%Y-%m-%dT%H:%M:%S.%f")
        self.dateCreation = self.metadata["dateCreation"]
        self.dataAcquisition = self.metadata["dataAcquisition"]
        self.metadata["clouds"] = 999
        self.metadata["angle"] = float(self.metadata["angle"])  
        self.metadata["quicklook"] = "PREVIEW.JPG"
        self.quicklookUrl = self.metadata["quicklook"]
        self.productname = self.metadata["product"]
        self.clouds = self.metadata["clouds"]
        self.angle = self.metadata["angle"]
        self.gridid = int(self.metadata["tileid"])   
        
        
    