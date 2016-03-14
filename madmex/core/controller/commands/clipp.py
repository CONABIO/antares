'''
Created on Mar 14, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import os

from osgeo import ogr

from madmex.core.controller.base import BaseCommand


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--shape', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--raster', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        shape_name = options['shape'][0]
        raster = options['raster'][0]

        print os.path.exists(shape_name)
        print raster

        driver = ogr.GetDriverByName(str('ESRI Shapefile'))
        shape = driver.Open(shape_name, 0)

        layer = shape.GetLayer()

        for feature in layer:
            print dir(feature)
            print feature.GetField(2)
