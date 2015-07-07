'''
Created on Jul 1, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.mapper.base import BaseParser, _xml_to_json
import xml.dom.minidom as dom


class Parser(BaseParser):
    '''
    This class represents a parser to process files from the World View sensor.
    Usually, World View Sensor comes with two metadata files so we will parse
    them both, and add them into a in memory json representation of them.
    '''
        
    def parse(self):
        document = dom.parse(self.filepath)
        stack = []
        self.metadata = {}
        _xml_to_json(document.documentElement, stack, self.metadata)    
