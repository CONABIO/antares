'''
madmex.mapper.sensor
'''
from __future__ import unicode_literals
from xml.dom.minidom import Document

from madmex import find_in_dir
from madmex import load_class

class DublinCoreMetadata(object):
    '''
    This class creates an instance of an object compliant with the Dublin Core
    specification found in:
    http://www.dublincore.org/documents/2003/04/02/dc-xml-guidelines/
    '''
    def __init__(self):
        self.title = ''
        self.creator = ''
        self.subject = ''
        self.description = ''
        self.publisher = ''
        self.contributor = ''
        self.date = ''
        self.type = ''
        self.format = ''
        self.identifier = ''
        self.source = ''
        self.language = ''
        self.relation = ''
        self.coverage = ''
        self.rights = ''
        self.about = ''
    def to_file(self, filename):
        '''
        This method writes the xml representation of this object in a file.
        '''
        xml_file = open(filename, 'wb')
        xml_file.write(self.to_xml_string())
        xml_file.close()
    def to_xml_string(self):
        '''
        This method returns an xml string representation of this object.
        '''
        return self._dublin_core_xml().toprettyxml()
    def _dublin_core_xml(self):
        '''
        This method creates an xml file using the dublin core standards.
        '''
        document = Document()
        metadata = document.createElement('metadata')
        metadata.setAttribute('xmlns', 'http://example.org/myapp/')
        metadata.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        document.appendChild(metadata)
        self._add_property(document, 'title')
        for name in dir(self):
            if not name.startswith('_') and not name.startswith('to'):
                self._add_property(document, name)
        return document
    def _add_property(self, document, attribute):
        '''
        This method tries to read the given attribute, if finds it, it adds an
        entry to the xml structure.
        '''
        local_attribute = getattr(self, attribute)
        metadata = document.getElementsByTagName('metadata')[0]
        if local_attribute:
            if not isinstance(local_attribute, list):
                attribute_list = [local_attribute]
            else:
                attribute_list = local_attribute
            for name in attribute_list:
                title = document.createElement('dc:%s' % attribute)
                metadata.appendChild(title)
                text = document.createTextNode(name)
                title.appendChild(text)
