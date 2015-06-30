'''
Created on 29/06/2015

@author: erickpalacios
'''
from madmex.processes.extractsensormetadata.base import BaseSensor
from datetime import datetime


class Sensor(BaseSensor):
    '''
    classdocs
    '''
    def __init__(self):
        self.sensor_name = 'spot5'
        self.tagList = {
                    "product" : ["Dimap_Document","Data_Processing","PROCESSING_LEVEL"],
                    "sensor" : ["Dimap_Document","Dataset_Sources","Scene_Source","MISSION"],
                    "platform" : ["Dimap_Document","Dataset_Sources","Scene_Source","MISSION_INDEX"],
                    "dateCreation" : ["Dimap_Document","Production","DATASET_PRODUCTION_DATE"],
                    "dataAcquisition" : ["Dimap_Document","Dataset_Sources","Scene_Source","IMAGING_DATE"],
                    "dataAcquisitionTime" : ["Dimap_Document","Dataset_Sources","Scene_Source","IMAGING_TIME"],
                    "angle": ["Dimap_Document","Dataset_Sources","Scene_Source","VIEWING_ANGLE"],
                    #"quicklook" : ["Dimap_Document","Dataset_Id","DATASET_QL_PATH"],
                    #"clouds": ["Dimap_Document","IMD","IMAGE","CLOUDCOVER"],
                    "tileid" : ["Dimap_Document","Dataset_Sources","Scene_Source","GRID_REFERENCE"]
                    }
        self.metadata=dict()
    def change_format(self, metadataStruct):
        try:
 
            self.metadataStruct = metadataStruct
            acquisitionDate = self.metadataStruct["dataAcquisition"]
            acquisitionTime = self.metadataStruct["dataAcquisitionTime"]
            creationDate = self.metadataStruct["dateCreation"]
            self.metadataStruct["dataAcquisition"] = datetime.strptime(acquisitionDate+"T"+acquisitionTime, "%Y-%m-%dT%H:%M:%S")
            
            self.metadataStruct["dateCreation"] = datetime.strptime(creationDate, "%Y-%m-%dT%H:%M:%S.%f")
            self.metadataStruct["angle"] = float(self.metadataStruct["angle"])
            
            self.metadataStruct["clouds"] = 999
            self.metadataStruct["quicklook"] = "PREVIEW.JPG"
            self.sensorname = self.metadataStruct["sensor"]
            self.productname = self.metadataStruct["product"]
            self.dateCreation = self.metadataStruct["dateCreation"]
            self.dataAcquisition = self.metadataStruct["dataAcquisition"]
            self.clouds = self.metadataStruct["clouds"]
            self.angle = self.metadataStruct["angle"]
            self.quicklookUrl = self.metadataStruct["quicklook"]
            self.gridid = int(self.metadataStruct["tileid"])                   
        except IOError:
            raise "Meta data extraction not successful"
        
    