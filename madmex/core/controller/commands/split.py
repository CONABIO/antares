# -*- coding: utf-8 -*-
'''
Created on Mar 14, 2016

@author: agutierrez
'''   

from __future__ import unicode_literals

import json
import logging
import os

import gdal
import numpy
from osgeo import ogr
from pandas.core.frame import DataFrame
from scipy.constants.constants import hectare
import simplejson

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.core.controller.commands.tth import area
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import create_filename_from_string, create_file_name, \
    create_directory_path, get_base_name


LOGGER = logging.getLogger(__name__)

NUM_CLASSES= 8 + 1

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
    shape_files = []
    
    while in_feature:
        encoding = 'utf-8'
        in_feature_name = create_filename_from_string(in_feature.GetField(column).decode(encoding))

        final_path = destination_directory + str(in_feature.GetField(0))
        create_directory_path(final_path)
        output_name = create_file_name(final_path, in_feature_name + '.shp')
        shape_files.append(output_name)

        if os.path.exists(output_name):
            driver.DeleteDataSource(output_name)
        datasource = driver.CreateDataSource(output_name)

        outLayer = datasource.CreateLayer(layer_name, spatial_reference, geom_type=ogr.wkbPolygon)

        inLayerDefn = layer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            #LOGGER.debug(fieldDefn.GetName())
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
    return shape_files
    
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

def calculate_thh(s1, s2, years):
    return 1 - (1 - (s1 - s2) * 1.0 / s1)**(1.0 / years)

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--path', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
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
        paths = options['path']
        
        years = []
        for path in paths:
            years.append(self.get_year_from_path(path))   

        
        if os.path.exists(shape_name):
            LOGGER.info('The file %s was found.' % shape_name)
        shape_files = split_shape_into_features(shape_name, destination, str('nombre'))
        process_launcher = LocalProcessLauncher()
        
        import time
        start_time = time.time()
        
        for shape_file in shape_files:
            basename = '%s.tif' % get_base_name(shape_file)
            cover_file = '%s.json' % get_base_name(shape_file)
            tth_name = '%s-tth.json' % get_base_name(shape_file)
            dataframe = DataFrame(index=years, columns=[0, 1, 2 ,3 , 4, 5, 6, 7, 8])
            json_directory = create_file_name(destination, 'cover_stats')
            create_directory_path(json_directory)
            json_file = create_file_name(json_directory, cover_file.lower())
            tth_file = create_file_name(json_directory, tth_name.lower())
            print shape_file
            for path in paths:
                #pixel_resolution, dataset = pixel_info(path)
                 
                
                year = self.get_year_from_path(path)
                raster_dir = create_file_name(create_file_name(destination, 'raster'), year)
                create_directory_path(raster_dir)
                raster_file = create_file_name(raster_dir, basename)
                
                shell_command =  'gdalwarp -ot Byte -co COMPRESS=LZW -cutline %s -crop_to_cutline %s %s' % (shape_file, path, raster_file)
                print shell_command
                print process_launcher.execute(shell_command)
                raster_array = open_handle(raster_file)
                
                ds = gdal.Open(raster_file) 
                geotransform = ds.GetGeoTransform()     
                x_resolution = geotransform[1]
                y_resolution = geotransform[5]
                pixel_area = abs(x_resolution * y_resolution)
                
                
                                
                unique_values =  numpy.unique(raster_array, return_counts=True)
                
                indexes = unique_values[0]
                counts = unique_values[1]
                
                for i in range(len(indexes)):
                    key = indexes[i]
                    dataframe.set_value(year, key, area(int(counts[i]), pixel_area))
            dataframe = dataframe.sort_index()
            columns = list(dataframe.columns.values)
            index = list(dataframe.index.values)

            print dataframe
            
            self.dataframe_to_json(json_file, dataframe)
            
            tth_dataframe = DataFrame(columns=columns)
            
            for i in range(len(index) - 1):
                label = '%s-%s' % (index[i],index[i + 1])
                tth_column = calculate_thh(dataframe.ix[i], dataframe.ix[i + 1], int(index[i + 1]) - int(index[i]))
                for j in range(len(tth_column)):
                    tth_dataframe.set_value(label, j, tth_column[j])
            tth_dataframe = tth_dataframe.sort_index()
            
            print tth_dataframe


            self.dataframe_to_json(tth_file, tth_dataframe)
        print("--- %s seconds ---" % (time.time() - start_time))
            
    
    def dataframe_to_json(self, filename, dataframe):
        columns = list(dataframe.columns.values)
        index = list(dataframe.index.values)
        final = {}
        data = []
        
        # I don't want to consider column cero as it will be no data value.
        for column in columns[1:-1]:
            col =  list(dataframe[column])
            data.append(col)
        
        
        final['labels'] = index
        final['series'] = data
        final['class'] = ['No Data',
                          'Bosques Templado',
                          'Selva Perennifolia, Subperennifolia, Caducifolia y Subcaducifolia',
                          'Matorral',
                          'Vegetación Menor y Pastizales',
                          'Tierras Agrícolas',
                          'Urbano y Contruido',
                          'Suelo Desnudo',
                          'Agua']
        with open(filename, 'w') as f:
            f.write(simplejson.dumps(final, ignore_nan=True, indent=4 * ' '))
        
        
    def get_year_from_path(self, path):
        return get_base_name(path)[19:23]
