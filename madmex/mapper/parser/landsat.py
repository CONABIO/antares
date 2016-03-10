'''
Created on Jun 30, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

import datetime
import logging

import requests

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseParser, put_in_dictionary, \
    parse_value, _xml_to_json, _get_attribute
import xml.dom.minidom as dom


LOGGER = logging.getLogger(__name__)

USGS_HTTP_SERVICE = 'http://earthexplorer.usgs.gov/EE/InventoryStream/pathrow?' + \
                    'start_path=%d&end_path=%d&start_row=%d&end_row=%d&sensor=' + \
                    '%s&start_date=%s&end_date=%s'

def _landsat_harmonizer(value):
    '''
    This method harmonizes between different type of landsat metadata files.
    '''
    value = value.replace('LANDSAT_7', 'Landsat7')
    value = value.replace('ETM', 'ETM+')
    return value
def _landsat_parse_value(value):
    '''
    This method overrides functionality of parse value to add harmonizer process.
    '''
    return parse_value(_landsat_harmonizer(value))
def _get_usgs_metadata(path, row, sensor, date):
    '''
    This method creates a url and builds a request with it. The response is then
    returned to the caller.
    '''
    print sensor
    if sensor == 'ETM+' or sensor == 'ETM+':
        date_object = datetime.datetime.strptime(date, getattr(SETTINGS, 'DATE_FORMAT'))
        date_lansat_change = datetime.datetime.strptime(
            '2003-04-01',
            getattr(SETTINGS, 'DATE_FORMAT')
            )
        if date_object > date_lansat_change:
            sensor_encoding = 'LANDSAT_ETM_SLC_OFF'
        else:
            sensor_encoding = 'LANDSAT_ETM'
    elif sensor == 'OLI_TIRS':
        sensor_encoding = 'LANDSAT_8'
    elif sensor == 'TM':
        sensor_encoding = 'LANDSAT_TM'
    usgs_url = USGS_HTTP_SERVICE % (path, path, row, row, sensor_encoding, date, date)
    LOGGER.debug('USGS metadata will be retrieved from %s.', usgs_url)
    request = requests.get(usgs_url)
    return request
class Parser(BaseParser):
    '''
    Parses landsat metadata files creating a memory representation of the
    properties found in there.
    '''
    def __init__(self, file_path):
        '''
        Constructor
        '''
        super(Parser, self).__init__(file_path)
        self.usgs_metadata = None
    def parse(self):
        '''
        The parse method for the landsat instance needs two different sources of
        metadata. The first source is the usual local file, using this, further
        information is obtained, and a request to the usgs server is created.
        The response is then parsed into a new dictionary.
        '''
        metadata = open(self.filepath, 'r')
        group_dictionary = {}
        groups = {}
        stack = []
        LOGGER.debug('File: %s will be parsed as Landsat metadata file.', self.filepath)
        for line in metadata.readlines():
            if "=" in line:
                key, value = line.split('=')
                if key.lower().strip() == 'group':
                    stack.append(value.strip())
                    #put_in_dictionary(groups, stack, {})
                elif key.lower().strip() == 'end_group':
                    if group_dictionary:
                        put_in_dictionary(groups, stack, group_dictionary)
                    stack.pop()
                    group_dictionary = {}
                else:
                    group_dictionary[key.strip()] = parse_value(value.strip())
        metadata.close()
        self.metadata = groups
        LOGGER.debug('File metadata has been parsed.')
        path = self.get_attribute([
            'L1_METADATA_FILE',
            'PRODUCT_METADATA',
            'WRS_PATH'
            ])
        row = self.get_attribute([
            'L1_METADATA_FILE',
            'PRODUCT_METADATA',
            'WRS_ROW'
            ])
        sensor = self.get_attribute([
            'L1_METADATA_FILE',
            'PRODUCT_METADATA',
            'SENSOR_ID'
            ])
        acquisition_date = self.get_attribute([
            'L1_METADATA_FILE',
            'PRODUCT_METADATA',
            'DATE_ACQUIRED']
            )
        request = _get_usgs_metadata(path, row, sensor, acquisition_date)
        document = dom.parseString(request.text)
        stack = []
        self.usgs_metadata = {}
        _xml_to_json(document.documentElement, stack, self.usgs_metadata)
        LOGGER.debug('USGS metadata has been parsed.')
    def get_attribute(self, path_to_metadata):
        '''
        Method that overrides the usual behavior of getting an attribute, this
        class has two dictionaries of metadata, if an attribute is requested,
        both should be inspected.
        '''
        attribute = BaseParser.get_attribute(self, path_to_metadata)
        if not attribute:
            attribute = _get_attribute(path_to_metadata, self.usgs_metadata)
        return attribute

