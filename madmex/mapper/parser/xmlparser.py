'''
Created on 25/06/2015

@author: erickpalacios
'''

from __future__ import unicode_literals

from pyexpat import ExpatError
import unicodedata
from xml.dom import minidom

from madmex.mapper.base import BaseParser


'''
TODO: Change the name of this file, parser is not adequate as the package
already contains that word, in the other hand, xml alone overwrites the 
'''

class Parser(BaseParser):
    '''
    classdocs
    '''

    def __init__(self, metadatapath, tagList):
        '''
        Constructor
        '''
        super(Parser, self).__init__(metadatapath)
        self.tagList = tagList
        self.metadata = dict()
    def parse(self):
        print "open", self.filepath
        try:
            datafile = minidom.parse(self.filepath)          
            for i in self.tagList.keys():
                lentagList = len(self.tagList[str(i)])
                elem = datafile.getElementsByTagName(self.tagList[str(i)][lentagList-1])
                self.metadata[str(i)] = unicodedata.normalize('NFKD', elem[0].firstChild.nodeValue).encode('ascii','ignore')
        except ExpatError:
            print 'error in xml metadata file:%s' % self.filepath
            raise


