'''
Created on Mar 14, 2016

@author: agutierrez
'''   

from __future__ import unicode_literals

import logging
import os

import gdal
from osgeo import ogr

from madmex.core.controller.base import BaseCommand
from madmex.util import create_filename_from_string, create_file_name, \
    create_directory_path, get_base_name


LOGGER = logging.getLogger(__name__)

def split_shape_into_features(shape_name, destination_directory, column):
    '''
    This method will take a input shape and iterate over its features, creating
    a new shape file with each one of them. It copies all the fields and the
    same spatial reference from the original file. The created files are saved
    in the destination directory using the number of the field given. 
    '''
    driver = ogr.GetDriverByName(str('ESRI Shapefile'))
    shape = driver.Open(shape_name, 0)
    layer = shape.GetLayer()
    layer_name = layer.GetName()
    spatial_reference = layer.GetSpatialRef()
    in_feature = layer.GetNextFeature()

    while in_feature:
        encoding = 'utf-8'
        in_feature_name = create_filename_from_string(in_feature.GetField(column).decode(encoding))

        final_path = destination_directory + str(in_feature.GetField(0))
        create_directory_path(final_path)
        output_name = create_file_name(final_path, in_feature_name + '.shp')

        if os.path.exists(output_name):
            driver.DeleteDataSource(output_name)
        datasource = driver.CreateDataSource(output_name)

        outLayer = datasource.CreateLayer(layer_name, spatial_reference, geom_type=ogr.wkbPolygon)

        inLayerDefn = layer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            LOGGER.debug(fieldDefn.GetName())
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
    
def get_convex_hull(shape_name, destination_directory):
    '''
    This method will read all objects from a shape file and create a new one
    with the convex hull of all the geometry points of the first.
    '''
    driver = ogr.GetDriverByName(str('ESRI Shapefile'))
    shape = driver.Open(shape_name, 0)
    layer = shape.GetLayer()
    layer_name = layer.GetName()
    spatial_reference = layer.GetSpatialRef()
    prefix = get_base_name(shape_name)
    output_name = create_file_name(destination_directory, '%s-hull.shp' % prefix)
    geometries = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in layer:
        geometries.AddGeometry(feature.GetGeometryRef())
    if os.path.exists(output_name):
        driver.DeleteDataSource(output_name)
    datasource = driver.CreateDataSource(output_name)
    out_layer = datasource.CreateLayer(str('states_convexhull'), spatial_reference, geom_type=ogr.wkbPolygon)
    out_layer.CreateField(ogr.FieldDefn(str('id'), ogr.OFTInteger))
    featureDefn = out_layer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(geometries.ConvexHull())
    feature.SetField(str('id'), 1)
    out_layer.CreateFeature(feature)
    shape.Destroy()
    datasource.Destroy()

def world_to_pixel(geotransform, x, y):
    '''
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    '''
    ulX = geotransform[0]
    ulY = geotransform[3]
    xDist = geotransform[1]
    yDist = geotransform[5]
    rtnX = geotransform[2]
    rtnY = geotransform[4]
    pixel = int((x - xDist) / xDist)
    line = int((y - ulY) / yDist)
    return (pixel, line)

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
        parser.add_argument('--dest', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        shape_name = options['shape'][0]
        destination = options['dest'][0]

        if os.path.exists(shape_name):
            LOGGER.info('The file %s was found.' % shape_name)


        get_convex_hull(shape_name, destination)
