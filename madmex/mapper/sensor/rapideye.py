'''
Created on 29/06/2015

@author: erickpalacios
'''
from datetime import datetime

from madmex.mapper.base import BaseSensor


class Sensor(BaseSensor):
    '''
    classdocs
    '''
    def __init__(self):
        self.sensor_name = 'rapideye'
        self.tagList = {
                    "product" : ["gml:metaDataProperty","re:EarthObservationMetaData","eop:productType"],
                    "sensor" : ["gml:using","eop:EarthObservationEquipment","eop:sensor","re:Sensor","eop:sensorType"],
                    "platform" : ["gml:using","eop:EarthObservationEquipment","eop:platform","eop:Platform","eop:serialIdentifier"],
                    "dataAcquisition" : ["gml:metaDataProperty","re:EarthObservationMetaData","eop:downlinkedTo","eop:DownlinkInformation","eop:acquisitionDate"],
                    "dateCreation" : ["gml:metaDataProperty","re:EarthObservationMetaData","eop:archivedIn","eop:ArchivingInformation","eop:archivingDate"],
                    "clouds": ["gml:resultOf","re:EarthObservationResult","opt:cloudCoverPercentage"],
                    "angle": ["gml:using","eop:EarthObservationEquipment","eop:acquisitionParameters","re:Acquisition","eop:incidenceAngle"],
                    "azimuthAngle": ["gml:using","eop:EarthObservationEquipment","eop:acquisitionParameters","re:Acquisition","re:azimuthAngle"],
                    "solarazimuth": ["gml:using","eop:EarthObservationEquipment","eop:acquisitionParameters","re:Acquisition","opt:illuminationAzimuthAngle"],
                    "solarzenith": ["gml:using","eop:EarthObservationEquipment","eop:acquisitionParameters","re:Acquisition","opt:illuminationElevationAngle"],
                    "quicklook" : ["gml:resultOf", "re:EarthObservationResult","eop:browse","eop:BrowseInformation", "eop:fileName"],
                    "tileid" : ["gml:metaDataProperty", "re:EarthObservationMetaData","re:tileId"]
                    }
        self.metadata = dict()
    def change_format(self):
        try:
            acquisitionDate = self.metadata["dataAcquisition"]
            creationDate = self.metadata["dateCreation"]            
            self.metadata["dataAcquisition"] = datetime.strptime(acquisitionDate, "%Y-%m-%dT%H:%M:%S.%fZ")
            self.metadata["dateCreation"] = datetime.strptime(creationDate, "%Y-%m-%dT%H:%M:%SZ")
            self.metadata["angle"] = float(self.metadata["angle"])
            
            self.metadata["clouds"] = float(self.metadata["clouds"])
            self.quicklookUrl = self.metadata["quicklook"]
            
            self.productname = self.metadata["product"]
            self.dateCreation = self.metadata["dateCreation"]
            self.dataAcquisition = self.metadata["dataAcquisition"]
            self.clouds = self.metadata["clouds"]
            self.angle = self.metadata["angle"]
            self.gridid = int(self.metadata["tileid"])

            self.azimuthAngle = self.metadata["azimuthAngle"]
            self.solarazimuth = self.metadata["solarazimuth"]
            self.solarzenith = self.metadata["solarzenith"]
        except IOError:
            raise "Meta data extraction not successful"
            