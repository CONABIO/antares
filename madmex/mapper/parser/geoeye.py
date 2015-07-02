'''
Created on Jul 1, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

import json
from madmex.mapper.base import BaseParser, xml_to_json
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
        xml_to_json(document.documentElement, stack, self.metadata)    

def main():
    parser = Parser('/LUSTRE/MADMEX/eodata/wv02/11/2012/2012-09-19/lv2a-multi-ortho/12SEP19190058-M2AS-053114634020_01_P001.XML')
    parser.parse()
    print parser.get_attribute(['isd','IMD','BAND_C','ULLAT'])
    #print json.dumps(parser.metadata, indent=4)
if __name__ == "__main__":
    main()