'''
Created on Jul 2, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

from madmex.mapper.base import BaseParser, put_in_dictionary
import xml.dom.minidom as dom


LOGGER = logging.getLogger(__name__)

PRODUCT = ["Dimap_Document","Data_Processing","PROCESSING_LEVEL"]
SENSOR = ["Dimap_Document","Dataset_Sources","Scene_Source","MISSION"]
PLATFORM = ["Dimap_Document","Dataset_Sources","Scene_Source","MISSION_INDEX"]
CREATION_DATE = ["Dimap_Document","Production","DATASET_PRODUCTION_DATE"]
ACQUISITION_DATE = ["Dimap_Document","Dataset_Sources","Scene_Source","IMAGING_DATE"]
ACQUISITION_TIME = ["Dimap_Document","Dataset_Sources","Scene_Source","IMAGING_TIME"]
ANGLE = ["Dimap_Document","Dataset_Sources","Scene_Source","VIEWING_ANGLE"]
TILE_ID = ["Dimap_Document","Dataset_Sources","Scene_Source","GRID_REFERENCE"]

class Parser(BaseParser):
    '''
    This class is a parser for Spot metadata. Spot metadata usually comes in xml
    format in a file with DIM ending. We parse spot in this way because, Spot
    is usually huge and are only interested in a few attributes.
    '''
    def parse(self):
        self.metadata = {}
        document = dom.parse(self.filepath)
        for attribute in [PRODUCT, SENSOR, PLATFORM, CREATION_DATE, ACQUISITION_DATE, ACQUISITION_TIME, ANGLE, TILE_ID]:
            values = document.getElementsByTagName(attribute[-1])
            if len(values) == 1:
                put_in_dictionary(self.metadata, attribute, values[0].firstChild.nodeValue)
            else:
                put_in_dictionary(self.metadata, attribute, [value.firstChild.nodeValue for value in values])
