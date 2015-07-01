'''
Created on Jul 1, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.mapper.base import BaseParser


class Parser(BaseParser):
    '''
    This class represents a parser to process files from the World View sensor.
    Usually, World View Sensor comes with two metadata files so we will parse
    them both, and add them into a in memory json representation of them.
    '''
        
    def parse(self):
        
        print 'here we parse the file.'
        print self.filepath
        

def main():
    parser = Parser('/LUSTRE/MADMEX/eodata/wv02/11/2012/2012-09-19/lv2a-multi-ortho/12SEP19190058-M2AS-053114634020_01_P001.XML')
    parser.parse()
    
if __name__ == "__main__":
    main()