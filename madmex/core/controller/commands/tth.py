'''
Created on Oct 21, 2016

@author: rmartinez
'''

from __future__ import unicode_literals
from decimal import Decimal
from madmex.core.controller.base import BaseCommand

import sys
import os
import argparse
import gdal
import numpy as np
import re
import logging



LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        
        '''
        #parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('tth', nargs='*', )
        parser.add_argument('--pathList', nargs=1, help='Raster file directory')
        

    def handle(self, **options):
        '''
        
        '''
        
        LOGGER.info('First line on log file')
        with open("file.log","a+") as f:
            f.write('Line')
            