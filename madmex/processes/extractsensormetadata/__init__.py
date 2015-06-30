
'''
Created on 10/06/2015

@author: erickpalacios
'''

from madmex.processes.base import Processes
from madmex.processes.extractsensormetadata.parser.xmlparser import XmlParser
import re
class Process(Processes):
    '''
    classdocs
    '''
    def __init__(self, diction):
        self.diction = diction
        self.metadata_path = self.diction['metadata']         
    def execute(self):
        xml_parser = '\.xml$|\.dim$'
        extension_metadata = self.getextension(self.metadata_path)
        obj_regex = re.search(xml_parser, extension_metadata)
        if obj_regex:
            print 'Xml parser'
            metadata = XmlParser(self.metadata_path)
            self.output = metadata.run()
        else:
            if self.extension_metadata == '.txt':
                print 'landsat parser'
            else:
                print 'no parser'