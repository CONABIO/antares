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
import pandas
from pandas.core.frame import DataFrame
import scipy.ndimage

from madmex.configuration import SETTINGS
from madmex.core.controller.base import BaseCommand
from madmex.mapper.data import vector, raster, vector_to_raster
from madmex.mapper.data.harmonized import harmonize_images
from madmex.util import create_file_name, \
    create_directory_path


LOGGER = logging.getLogger(__name__)

NUM_CLASSES= 8 + 1

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

def get_dataframe_from_raster(features_raster, training_raster_warped):
    harmonize = harmonize_images([training_raster_warped, features_raster])
    LOGGER.info(harmonize)        
    training_array = training_raster_warped.read(int(harmonize['x_offset'][0]), int(harmonize['y_offset'][0]), int(harmonize['x_range']), int(harmonize['y_range']))
    features_array = features_raster.read(int(harmonize['x_offset'][1]), int(harmonize['y_offset'][1]), int(harmonize['x_range']), int(harmonize['y_range']))
    labels = numpy.unique(training_array)
    labels = labels[labels!=-9999]
    labels = labels[labels!=0]
    array_aux = []
    array_aux.append(labels)
    for i in range(features_array.shape[0]):
        mean_array = scipy.ndimage.measurements.mean(features_array[i,:,:], training_array, labels)
        array_aux.append(mean_array)
    for i in range(features_array.shape[0]):
        std_array = scipy.ndimage.measurements.standard_deviation(features_array[i,:,:], training_array, labels)
        array_aux.append(std_array)
    features_final = numpy.concatenate([array_aux], axis=0)        
    return DataFrame(features_final.transpose())
        
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
        import time
        start_time = time.time()
        shape_name = options['shape'][0]
        raster_path = options['path'][0]
        temporary_directory = getattr(SETTINGS, 'TEMPORARY')
        create_directory_path(temporary_directory)
        # I read the training data in shape form
        training_shape = vector.Data(shape_name)
        training_dataframe = training_shape.to_dataframe()
        training_path = create_file_name(temporary_directory, 'training_raster.tif')
        training_warped_path = create_file_name(temporary_directory, 'training_warped_raster.tif')
        pixel_size = 5
        training_raster = vector_to_raster(training_shape, training_path, pixel_size)
        features_raster = raster.Data(raster_path)
        training_raster_warped = training_raster.reproject(training_warped_path, epgs=32614)
        dataframe_features = get_dataframe_from_raster(features_raster, training_raster_warped)
        training_set = dataframe_features.set_index(0).join(training_dataframe.set_index('OBJECTID'))   
        training_set['target'] = pandas.Categorical.from_array(training_set['level_3']).labels
        print training_set        
        print("--- %s seconds ---" % (time.time() - start_time))
