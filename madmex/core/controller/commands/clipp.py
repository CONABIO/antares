'''
Created on Mar 14, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import os

from osgeo import ogr
import osr

from madmex.core.controller.base import BaseCommand
from madmex.util import create_filename_from_string, create_file_name


def split_shape_into_features(shape_name, destination_directory, column):
    driver = ogr.GetDriverByName(str('ESRI Shapefile'))
    shape = driver.Open(shape_name, 0)
    layer = shape.GetLayer()
    layer_name = layer.GetName()
    spatial_reference = layer.GetSpatialRef()
    

    
    in_feature = layer.GetNextFeature()
    
    while in_feature:
        
        
        encoding = 'utf-8'
        in_feature_name = create_filename_from_string(in_feature.GetField(column).decode(encoding))
        output_name = create_file_name(destination_directory, in_feature_name + '.shp')
        
        if os.path.exists(output_name):
            driver.DeleteDataSource(output_name)
        datasource = driver.CreateDataSource(output_name)
    
        outLayer = datasource.CreateLayer(layer_name, spatial_reference, geom_type=ogr.wkbPolygon)
    
        inLayerDefn = layer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)
        
        outLayerDefn = outLayer.GetLayerDefn()
        
        
        
        geometry = in_feature.GetGeometryRef()
        
        out_feature = ogr.Feature(outLayerDefn)
        out_feature.SetGeometry(geometry)
        
        for i in range(0, outLayerDefn.GetFieldCount()):
            out_feature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), in_feature.GetField(i))
            
        outLayer.CreateFeature(out_feature)
        out_feature.Destroy()
        in_feature.Destroy()
        in_feature = layer.GetNextFeature()
    shape.Destroy()
    datasource.Destroy()
    
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

        split_shape_into_features(shape_name,'/Users/amaury/Documents/anp/splited/', 2)
            