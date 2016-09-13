#!/usr/bin/env python
# encoding: utf-8
'''
Created on August 13, 2016
@author:     rmartinez
'''
# gdaldem hillshade /Users/rmartinez/Desktop/chiapas_to_hill.asc /Users/rmartinez/Documents/presentacion_secretarios/mapas/chiapas_shapehill3.asc -z 3.0 -s 1.0 -az 315.0 -alt 45.0 -of AAIGrid

from __future__ import unicode_literals
from madmex.core.controller.base import BaseCommand
from subprocess import Popen, PIPE

import subprocess
import logging

LOGGER = logging.getLogger(__name__)

def warp(args):
    """subprocess call"""
    
    options = ['/usr/bin/gdadem']
    options.extend(args)
    
    subprocess.check_call(options)


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the hillshade argument for this command
        '''
        
        parser.add_argument('hillshade', nargs=3, help='This is a test')


    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        
        val_0 = int(options['hillshade'][0])
        val_1 = int(options['hillshade'][1])
        val_2 = int(options['hillshade'][2])
        
        LOGGER.info('The val_0 is = %s ' % val_0)
        LOGGER.info('The val_1 is = %s ' % val_1)
        LOGGER.info('The val_2 is = %s ' % val_2)
        
        
            


