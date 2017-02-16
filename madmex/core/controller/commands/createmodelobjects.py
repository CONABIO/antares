# -*- coding: utf-8 -*-
'''
Created on Mar 14, 2016

@author: agutierrez
'''   

from __future__ import unicode_literals

import json
import logging
import os
import time
import traceback

import gdal
import numpy
import pandas
from pandas.core.frame import DataFrame
import scipy.ndimage
from sklearn.cross_validation import train_test_split

from madmex import load_class
from madmex.configuration import SETTINGS
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.createmodel import SUPERVISED_PACKAGE
from madmex.mapper.bundle import rapideye
from madmex.mapper.data import vector, raster, vector_to_raster, \
    raster_to_vector_mask
from madmex.mapper.data._gdal import create_raster_from_reference
from madmex.mapper.data.harmonized import harmonize_images
from madmex.util import create_file_name, \
    create_directory_path, get_base_name, json_to_file, is_file


LOGGER = logging.getLogger(__name__)

NUM_CLASSES= 8 + 1

LOGGER = logging.getLogger(__name__)

def save_to_file(data, filename):
    dataframe = pandas.DataFrame(data)
    dataframe.to_csv(filename, sep=str(','), encoding='utf-8', index = False, header = False)

def load_model(name):
    '''
    Loads the python module with the given name found in the path.
    '''
    try:
        module = load_class(SUPERVISED_PACKAGE, name)
        return module
    except Exception:
        traceback.print_exc()
        LOGGER.debug('No %s model found.', name)
        
def train_model(X_train, X_test, y_train, y_test, output, model_name):
    model = load_model(model_name)
    persistence_directory = create_file_name(output, model_name)
    create_directory_path(persistence_directory)
    model_instance = model.Model(persistence_directory)
    model_instance.fit(X_train, y_train)
    model_instance.save(persistence_directory)
    predicted = model_instance.predict(X_test)
    model_instance.create_report(y_test, predicted, create_file_name(persistence_directory, 'report.txt'))


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
    
    if harmonize['x_range'] < 0 or harmonize['y_range'] < 0:
        return None
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
def create_categories_file(filename, categories_array):
    dictionary = {}
    for i in range(len(categories_array)):
        dictionary[i] = categories_array[i]
    json_to_file(filename, dictionary)
    
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
        parser.add_argument('--model', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        target_tag = 'level_3'
        start_time_all = time.time()
        shape_name = options['shape'][0]
        raster_paths = options['path']
        destination = options['dest']
        models = options['model']
        dataframe_features = None
        temporary_directory = getattr(SETTINGS, 'TEMPORARY')
        create_directory_path(temporary_directory)
        # I read the training data in shape form
        training_shape = vector.Data(shape_name)
        training_dataframe = training_shape.to_dataframe()
        training_path = create_file_name(temporary_directory, 'training_raster.tif')
        categories_file = create_file_name(temporary_directory, 'categories.json')
        training_warped_path = create_file_name(temporary_directory, 'training_warped_raster.tif')
        pixel_size = 5
        
        if not is_file(training_warped_path):
            training_raster = vector_to_raster(training_shape, training_path, pixel_size, ['ATTRIBUTE=OBJECTID','COMPRESS=LZW'])
            training_raster_warped = training_raster.reproject(training_warped_path, epgs=32613)
        else:
            training_raster_warped = raster.Data(training_warped_path)
        
        dem_file = getattr(SETTINGS, 'DEM')
        
        dem_raster = raster.Data(dem_file)
        print dem_raster.get_spatial_reference()
        print 'reproyecting raster'
        #dem_raster_warped = dem_raster.reproject(training_warped_path, epgs=32614)
        
        #training_raster_warped = raster.Data(training_path)
        
        aspect_file = getattr(SETTINGS, 'ASPECT')
        slope_file = getattr(SETTINGS, 'SLOPE')

        
        
        print dem_file, aspect_file, slope_file
         
        
        for raster_path in raster_paths:
            scene_bundle = rapideye.Bundle(raster_path)
            
            raster_mask = scene_bundle.get_raster()

            #example_path = create_file_name(temporary_directory, 'mask')
            #create_directory_path(example_path)
            #raster_to_vector_mask(raster_mask, example_path)
            
            
            
            
            basename = get_base_name(scene_bundle.get_raster_file())
            all_file = create_file_name(temporary_directory, '%s_all_features.tif' % basename)
            # Do not recalculate if the file is already there.
            if is_file(all_file):
                features_raster =raster.Data(all_file)
            else:
                features_raster = scene_bundle.get_feature_array(all_file)
            new_df = get_dataframe_from_raster(features_raster, training_raster_warped)
            if new_df is not None:
                if dataframe_features is not None:                               
                    dataframe_features = pandas.concat([dataframe_features, get_dataframe_from_raster(features_raster, training_raster_warped)])
                else:
                    dataframe_features = get_dataframe_from_raster(features_raster, training_raster_warped)
        
        features_size = len(list(dataframe_features))
        
        
        
        training_set = dataframe_features.set_index(0).join(training_dataframe.set_index('OBJECTID'))   
        
        
        
        training_set['target'] = pandas.Categorical.from_array(training_set[target_tag]).labels
        categories_array = pandas.Categorical.from_array(training_set[target_tag]).categories
        create_categories_file(categories_file, categories_array)
        training_set = training_set[training_set['target'] != -1]
        #features_size includes 0 that is the index of the feature
        training_set_array = numpy.transpose(numpy.transpose(training_set.as_matrix([range(1, features_size)])))
        target_set_array = training_set.pop('target')
        
        print training_set_array.shape
        print target_set_array.shape
        
        
        
        
        X_train, X_test, y_train, y_test = train_test_split(training_set_array, target_set_array, train_size=0.8, test_size=0.2)
        models_directory = create_file_name(temporary_directory, 'models')
        create_directory_path(models_directory)
        
        for model_name in models:
            start_time = time.time()
            print numpy.unique(y_train)
            train_model(X_train, X_test, y_train, y_test, models_directory, model_name)
            print "--- %s seconds training %s model---" % ((time.time() - start_time), model_name)
