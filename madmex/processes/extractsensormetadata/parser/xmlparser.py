
'''
Created on 25/06/2015

@author: erickpalacios
'''
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import xml.sax, csv
from madmex import load_class
import numpy
import unicodedata

SENSORS_PACKAGE = 'madmex.processes.extractsensormetadata.sensor'

class XmlParser(object):
    '''
    classdocs
    '''


    def __init__(self, metadata_path):
        '''
        Constructor
        '''
        self.metadata_path=metadata_path
    def get_type(self, filename):
        if """<?xml version="1.0"?>""" in filename:
            return "xml"
        print "open ",filename
        with open(filename, 'rb') as fh:
            try:
                xml.sax.parse(fh, xml.sax.ContentHandler())
                return 'xml'
            except: 
                pass
            fh.seek(0)
            try:
                for line in csv.reader(fh):
                    pass
                return 'csv'
            except csv.Error:
                pass
    
            return 'txt'
    
    def run(self):
        if self.get_type(self.metadata_path) == "xml":
            try:
                datafile = minidom.parseString(self.metadata_path)

            except ExpatError, e:
                datafile = minidom.parse(self.metadata_path)
            if datafile.getElementsByTagName('Dimap_Document'):
                sensor_class = load_class(SENSORS_PACKAGE, 'spot').Sensor()
            else:
                if datafile.getElementsByTagName('re:EarthObservationMetaData'):
                    sensor_class = load_class(SENSORS_PACKAGE, 'rapideye').Sensor()            
            for i in sensor_class.tagList.keys():
                elem = datafile
                for j in xrange(numpy.size(sensor_class.tagList[str(i)])):
                    elem = elem.getElementsByTagName(sensor_class.tagList[str(i)][j])
                    elem = elem[0]
                sensor_class.metadata[str(i)] = unicodedata.normalize('NFKD', elem.firstChild.nodeValue).encode('ascii','ignore')
            
            sensor_class.change_format(sensor_class.metadata)
            return sensor_class