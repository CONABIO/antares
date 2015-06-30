'''
Created on 30/06/2015

@author: erickpalacios
'''
import uuid

class BaseSensor(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.base_directory = None
        self.sensorType = None
        self.dateCreation = None
        self.dataAcquisition = None      
        self.uuid = uuid.uuid4()
        self.gridid = None
        self.format = "not set"
        self.sensor = None
        self.sensorname = None
        self.platform = None
        self.product = "not set"
        self.productname = None
        self.clouds = None
        self.nodata = -1
        self.angle = None
        self.solarazimuth = 0
        self.solarzenith = 0
        
    def change_format(self):
        """
        Change format of various values
     
        """
        pass


        