'''
Created on 25/06/2015

@author: erickpalacios
'''

from __future__ import unicode_literals

from madmex.mapper.base import BaseParser, _xml_to_json
import xml.dom.minidom as dom

class Parser(BaseParser):
    '''
    This class implements a parser for RapidEye metadata. RapidEye metadata
    comes in a simple xml file so we can just call the xml parser to create
    a in memory representation using a dictionary.
    '''
    def parse(self):
        '''
        Opens the metadata file and creates a json representation of it.
        '''
        self.metadata = {}
        document = dom.parse(self.filepath)
        stack = []
        self.metadata = {}
        _xml_to_json(document.documentElement, stack, self.metadata)
