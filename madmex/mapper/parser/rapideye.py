'''
Created on 25/06/2015

@author: erickpalacios
'''

from __future__ import unicode_literals

from madmex.mapper.base import BaseParser, _xml_to_json
import xml.dom.minidom as dom


class Parser(BaseParser):
    '''
    classdocs
    '''

    def parse(self):
        self.metadata = {}
        document = dom.parse(self.filepath)
        stack = []
        self.metadata = {}
        _xml_to_json(document.documentElement, stack, self.metadata)
