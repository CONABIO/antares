'''
Created on Jun 30, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

import json
import logging

from madmex.mapper.base import BaseParser, ParseError, put_in_dictionary, \
    parse_value


LOGGER = logging.getLogger(__name__)

def _landsat_harmonizer(value):
    '''
    This method harmonizes between different type of landsat metadata files.
    '''
    value = value.replace("LANDSAT_7", "Landsat7")
    value = value.replace('ETM"', 'ETM+"')
    return value
def _landsat_parse_value(value):
    '''
    This method overrides functionality of parse value to add harmonizer process.
    '''
    return parse_value(_landsat_harmonizer(value))

class Parser(BaseParser):
    '''
    Parses landsat metadata files creating a memory representation of the
    properties found in there.
    '''         
    def parse(self):
        metadata = open(self.filepath, "r")
        group_dictionary = {}
        groups = {}
        stack = []
        LOGGER.debug("File: %s will be parsed as Landsat metadata file." % self.filepath)
        for line in metadata.readlines():
           
            if "=" in line:
                key, value = line.split(" = ")
                if "group" == key.lower().strip():
                    stack.append(value.strip())
                    put_in_dictionary(groups, stack, {})
                elif "end_group" == key.lower().strip():
                    if group_dictionary:
                        put_in_dictionary(groups, stack, group_dictionary)
                    stack.pop()
                    group_dictionary = {}
                else:
                    group_dictionary[key.strip()] = parse_value(value.strip())
        metadata.close()
        self.metadata = groups
    def get_attribute(self):
        '''
        This method gets an attribute from the parser object that represents
        a field in the real world object that is being parsed.
        '''
        if not self.metadata:
            raise ParseError(
                'The file has not being parsed yet, please call parse() method'
                )
def main():
    '''
    TODO: remove this, this is just for testing purposes
    '''
    metadata = "/LUSTRE/MADMEX/eodata/etm+/25046/2013/2013-04-03/l1t/LE70250462013093ASN00_MTL.txt"
    parser = Parser(metadata)
    parser.parse()
    print json.dumps(parser.metadata, indent=4)
if __name__ == "__main__":
    main()
