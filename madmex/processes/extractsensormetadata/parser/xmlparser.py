#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 25/06/2015

@author: erickpalacios
'''
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import unicodedata

class XmlParser(object):
    '''
    classdocs
    '''

    def __init__(self, metadata_path, tagList):
        '''
        Constructor
        '''
        self.metadata_path=metadata_path
        self.tagList = tagList

    def run(self, metadata):
        #metadata is an empty dictionary of a sensor
        print "open", self.metadata_path
        try:
            datafile = minidom.parse(self.metadata_path)          
            for i in self.tagList.keys():
                len_tagList = len(self.tagList[str(i)])
                elem = datafile.getElementsByTagName(self.tagList[str(i)][len_tagList-1])
                metadata[str(i)] = unicodedata.normalize('NFKD', elem[0].firstChild.nodeValue).encode('ascii','ignore')
        except ExpatError:
            print 'error in xml metadata file:%s' % self.metadata_path
            raise