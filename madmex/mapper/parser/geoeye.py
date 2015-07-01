'''
Created on Jul 1, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.mapper.base import BaseParser
import xml.dom.minidom as dom

def xml_to_txt(node, stack):
    print stack
    stack.append(node.nodeName)
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            if child.data:
                print node.nodeName,child.data
            
            
        if child.nodeType == dom.Node.ELEMENT_NODE:
            xml_to_txt(child, stack)
            stack.pop()

def process_child(node):
    print node.tagName
    for child in node.childNodes:
        process_child(child)

class Parser(BaseParser):
    '''
    This class represents a parser to process files from the World View sensor.
    Usually, World View Sensor comes with two metadata files so we will parse
    them both, and add them into a in memory json representation of them.
    '''
        
    def parse(self):
        document = dom.parse(self.filepath)
        stack = []
        xml_to_txt(document.documentElement, stack)
        
        #process_child(document.childNodes[0])
        

def main():
    parser = Parser('/LUSTRE/MADMEX/eodata/wv02/11/2012/2012-09-19/lv2a-multi-ortho/12SEP19190058-M2AS-053114634020_01_P001.XML')
    parser.parse()
    
if __name__ == "__main__":
    main()