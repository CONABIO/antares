#!/usr/bin/env python
# encoding: utf-8
'''
Created on August 13, 2016
@author:     rmartinez

This class implements the gdaldem function hillshade. It is mandatory 
a Digital Elevation Model (DEM) file. It is possible to download from
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
        Adds the hillshade argument for this command
        '''
        parser.add_argument('hillshade', nargs='*', help='Hillshade option for gdaldem command')
        parser.add_argument('--inFile', nargs='*',help='Input file')
        parser.add_argument('--outFile', nargs='*',help='Output file')
        parser.add_argument('--z', nargs=1, help='z factor')
        parser.add_argument('--scale', nargs=1, help='scale')
        parser.add_argument('--az', nargs=1, help='azimuth')
        parser.add_argument('--alt', nargs=1, help='altitude')


    def handle(self, **options):
        '''
        A gdalinfo call is performed to check the input file, then, a gdaldem function with hillshade 
        option is called. The result is printed in the screen and written in the output file with
        GTiff format.
        '''
        
        inputFile  = options['inFile'][0]
        outputFile = options['outFile'][0]
        z_factor   = options['z'][0]
        scale      = options['scale'][0]
        azimuth    = options['az'][0]
        altitude   = options['alt'][0]
        
        
        if os.path.exists(inputFile):
            LOGGER.info('The file %s was found.' % inputFile)
        else:
            LOGGER.error('Input file not found')
            sys.exit(1)
                
        LOGGER.info('The input file is       : %s   ' %inputFile)
        LOGGER.info('The output file will be : %s  ' %outputFile)
        LOGGER.info('The z_factor is         : %s  ' %z_factor)
        LOGGER.info('The scale is            : %s  ' %scale)
        LOGGER.info('The azimuth is          : %s  ' %azimuth)
        LOGGER.info('The altitude is         : %s  ' %altitude)

        
        try:
            subprocess.check_call(['gdalinfo', inputFile])
        except subprocess.CalledProcessError:
            pass
            
        try:
            subprocess.check_call(['gdaldem',
                                   'hillshade', 
                                   inputFile, 
                                   outputFile, 
                                   '-z', z_factor, 
                                   '-s', scale, 
                                   '-az', azimuth, 
                                   '-alt', altitude,
                                   '-of', 'GTiff'])
        except subprocess.CalledProcessError:
            pass
        
        
            


