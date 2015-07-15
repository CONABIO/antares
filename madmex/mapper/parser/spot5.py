'''
Created on Jul 2, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

from madmex.mapper.base import BaseParser, put_in_dictionary
import xml.dom.minidom as dom


LOGGER = logging.getLogger(__name__)

class Parser(BaseParser):
    '''
    This class is a parser for Spot metadata. Spot metadata usually comes in xml
    format in a file with DIM ending. We parse spot in this way because, Spot
    is usually huge and are only interested in a few attributes.
    '''
    def __init__(self, metadata_path, metadata_list):
        '''
        Constructor
        '''
        super(Parser, self).__init__(metadata_path)
        self.metadata_list = metadata_list
        self.metadata = {}
    def parse(self):
        '''
        Spot metadata file is rather complex, instead of parsing the whole file,
        only a few attributes are looked up and added to the metadata dictionary.
        In the future it might be desirable to implement a full parser for this
        sensor. Specifications for the metadata xml file can be found in:
        http://www.spotimage.fr/dimap/spec/dictionary/Spot_Scene/DIMAP_DOCUMENT.htm
        '''
        document = dom.parse(self.filepath)
        for attribute in self.metadata_list:
            values = document.getElementsByTagName(attribute[-1])
            if len(values) == 1:
                put_in_dictionary(self.metadata, attribute, values[0].firstChild.nodeValue)
            else:
                put_in_dictionary(
                    self.metadata,
                    attribute,
                    [value.firstChild.nodeValue for value in values]
                    )
