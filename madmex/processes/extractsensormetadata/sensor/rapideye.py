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
    def change_format(self, metadataStruct):

        try:
            self.metadataStruct = metadataStruct


            acquisitionDate = self.metadataStruct["dataAcquisition"]
            creationDate = self.metadataStruct["dateCreation"]
            angle = self.metadataStruct["angle"]
            clouds = self.metadataStruct["clouds"]
            self.metadataStruct["dataAcquisition"] = datetime.strptime(acquisitionDate, "%Y-%m-%dT%H:%M:%S.%fZ")
            self.metadataStruct["dateCreation"] = datetime.strptime(creationDate, "%Y-%m-%dT%H:%M:%SZ")
            self.metadataStruct["angle"] = float(angle)
            self.metadataStruct["clouds"] = float(clouds)
            print self.metadataStruct["clouds"]
        except IOError:
            raise "Meta data extraction not successful"
            