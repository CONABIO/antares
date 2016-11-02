#!/usr/bin/env python
# encoding: utf-8
'''
Created on August 15, 2016
@author:     rmartinez

This class implements the gdal_contour function. A Digital Elevation Model 
(DEM) file is mandatory. It is possible to download from
http://www.inegi.org.mx/geo/contenidos/datosrelieve/continental/Descarga.aspx
for Mexico.
'''

from __future__ import unicode_literals
from madmex.core.controller.base import BaseCommand

import subprocess
import logging
import os
import sys

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the contour argument for this command
        '''
        parser.add_argument('contour', nargs='*', help='Gdal contour-line command')
        parser.add_argument('--inFile', nargs='*',help='Input file')
        parser.add_argument('--outFile', nargs='*',help='Output file')
        parser.add_argument('--delta', nargs=1, help='Interval between contour lines in meters')
       

    def handle(self, **options):
        '''
        A gdalinfo call is performed to check the input file, then, gdal_contour function 
        is called. The result is printed in the screen and written in the output file with
        ESRI shapefile format.
        '''
        
        inputFile  = options['inFile'][0]
        outputFile = options['outFile'][0]
        delta      = options['delta'][0]
        
        
        if os.path.exists(inputFile):
            LOGGER.info('The file %s was found.' % inputFile)
        else:
            LOGGER.error('Input file not found')
            sys.exit(1)
        
        # gdal_contour does not works if output file already exist. 
        if os.path.exists(outputFile):
            LOGGER.warning('File %s already exist.' % outputFile)
            LOGGER.info('Deleting existing file')
            try :
                os.remove(outputFile) 
            except :
                LOGGER.error('Impossible to delete %s' %outputFile + ' consider to change output file.' )
                sys.exit(1)
            LOGGER.info('Succesfully deleted')
        
            
        LOGGER.info('The input file is             : %s  ' %inputFile)
        LOGGER.info('The output file will be       : %s  ' %outputFile)
        LOGGER.info('The interval between lines is : %s  ' %delta + '[m]')
         
         
        try:
            subprocess.check_call(['gdalinfo', inputFile])
        except subprocess.CalledProcessError:
            pass
              
        try:
            subprocess.check_call(['gdal_contour',
                                   '-a',
                                   'ELEV',
                                   '-i', 
                                   delta,
                                   inputFile, 
                                   outputFile])
        except subprocess.CalledProcessError:
            pass
        