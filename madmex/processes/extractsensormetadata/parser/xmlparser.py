
'''
Created on 25/06/2015

@author: erickpalacios
'''
from madmex import load_class
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import unicodedata

SENSORS_PACKAGE = 'madmex.mapper.sensor'

class XmlParser(object):
    '''
    classdocs
    '''

    def __init__(self, metadata_path):
        '''
        Constructor
        '''
        self.metadata_path=metadata_path

    def run(self):
        print "open", self.metadata_path
        try:
            datafile = minidom.parse(self.metadata_path)
            if datafile.getElementsByTagName('Dimap_Document'):
                sensor_class = load_class(SENSORS_PACKAGE, 'spot').Sensor()
            else:
                if datafile.getElementsByTagName('re:EarthObservationMetaData'):
                    sensor_class = load_class(SENSORS_PACKAGE, 'rapideye').Sensor()            
            for i in sensor_class.tagList.keys():
                len_tagList = len(sensor_class.tagList[str(i)])
                elem = datafile.getElementsByTagName(sensor_class.tagList[str(i)][len_tagList-1])
                sensor_class.metadata[str(i)] = unicodedata.normalize('NFKD', elem[0].firstChild.nodeValue).encode('ascii','ignore')
            sensor_class.change_format()
            return sensor_class
        except ExpatError:
            print 'error in xml metadata file:%s' % self.metadata_path
            raise