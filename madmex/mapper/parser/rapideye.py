'''
Created on 25/06/2015

@author: erickpalacios
'''

from __future__ import unicode_literals

from pyexpat import ExpatError
import unicodedata
from xml.dom import minidom
from madmex.mapper.base import BaseParser

class Parser(BaseParser):
    '''
    classdocs
    '''

    def __init__(self, metadata_path, metadata):
        '''
        Constructor
        '''
        super(Parser, self).__init__(metadata_path)
        self.metadata = metadata
    def parse(self):
        print "open", self.filepath
        try:
            datafile = minidom.parse(self.filepath)          
            for i in self.metadata.keys():
                elem = datafile.getElementsByTagName(self.metadata[i])
                self.metadata[i] = unicodedata.normalize('NFKD', elem[0].firstChild.nodeValue).encode('ascii','ignore')
        except ExpatError:
            print 'error in xml metadata file:%s' % self.filepath
            raise
