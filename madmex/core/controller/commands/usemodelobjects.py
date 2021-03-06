'''
Created on Nov 21, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import logging
import os
import time
import warnings

import gdal
import numpy
import ogr
from sklearn.externals import joblib

from madmex import _
from madmex.configuration import SETTINGS
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.createmodel import load_model
from madmex.core.controller.commands.indexes import open_handle
from madmex.core.controller.commands.ingest import _get_bundle_from_path
from madmex.mapper.bundle import rapideye
from madmex.mapper.data import raster
from madmex.mapper.data._gdal import create_raster_from_reference
from madmex.model.unsupervised import pca
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import create_filename, get_basename, create_directory_path, \
    get_parent, is_file, create_filename_from_string, json_from_file


LOGGER = logging.getLogger(__name__)

def read_data_table(shape_path):
    driver = ogr.GetDriverByName(str('ESRI Shapefile'))
    shape = driver.Open(shape_path, 0)
    layer = shape.GetLayer()
    in_feature = layer.GetNextFeature()

    table = []
    while in_feature:
        inLayerDefn = layer.GetLayerDefn()
        obs = []
        for i in range(2, inLayerDefn.GetFieldCount()):
            field = in_feature.GetField(i)
            obs.append(field)
        table.append(obs)
        in_feature.Destroy()
        in_feature = layer.GetNextFeature()
    result = numpy.array(table)    
    return result

def write_results(shape_path, output_name, classification, classification_dict, epsg=32613):
    driver = ogr.GetDriverByName(str('ESRI Shapefile'))
    shape = driver.Open(shape_path, 0)
    layer = shape.GetLayer()
    #spatial_reference = layer.GetSpatialRef()
    spatial_reference = ogr.osr.SpatialReference()
    spatial_reference.ImportFromEPSG(epsg)
    in_feature = layer.GetNextFeature()

    counter=0

    if os.path.exists(output_name):
        driver.DeleteDataSource(output_name)
    datasource = driver.CreateDataSource(output_name)
    outLayer = datasource.CreateLayer(str('classification'), spatial_reference, geom_type=ogr.wkbPolygon)        
    for model_name, data in classification.iteritems():
        idField = ogr.FieldDefn(str(model_name.upper()), ogr.OFTString)
        outLayer.CreateField(idField)
        idField = ogr.FieldDefn(str('%sLABEL' % model_name.upper()), ogr.OFTInteger)
        outLayer.CreateField(idField)
    while in_feature:
        
        featureDefn = outLayer.GetLayerDefn()
        geometry = in_feature.GetGeometryRef()
        
        out_feature = ogr.Feature(featureDefn)
        out_feature.SetGeometry(geometry)
    
        for model_name, data in classification.iteritems():
            out_feature.SetField(str(model_name.upper()), str(classification_dict[data[counter]]))
            out_feature.SetField(str('%sLABEL' % model_name.upper()), int(data[counter]))
  
        outLayer.CreateFeature(out_feature)
        out_feature.Destroy()
        in_feature.Destroy()
        in_feature = layer.GetNextFeature()
        counter = counter + 1
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
        parser.add_argument('--path', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--output', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--modelname', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--modeldir', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--region', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        output = options['output'][0]
        models = options['modelname']
        model_directory = options['modeldir'][0]
        region = options['region'][0]
        
        start_time = time.time()
        
        for path in options['path']:
            print path
            
            scene_bundle = rapideye.Bundle(path)
            directory = getattr(SETTINGS, 'TEMPORARY')
            directory_helper = create_filename(directory, 'helper')
            create_directory_path(directory_helper)
            categories_file = create_filename(directory, 'categories.json')
            categories_dictionaty = {
                    0: "AGRICULTURA DE RIEGO", 
                    1: "AGRICULTURA DE TEMPORAL", 
                    2: "AGUA", 
                    3: "AREAS QUEMADAS", 
                    4: "ASENTAMIENTOS HUMANOS", 
                    5: "BOSQUE CULTIVADO", 
                    6: "BOSQUE DE AYARIN", 
                    7: "BOSQUE DE ENCINO", 
                    8: "BOSQUE DE ENCINO-PINO", 
                    9: "BOSQUE DE GALERIA", 
                    10: "BOSQUE DE MEZQUITE", 
                    11: "BOSQUE DE OYAMEL", 
                    12: "BOSQUE DE PINO", 
                    13: "BOSQUE DE PINO-ENCINO", 
                    14: "BOSQUE INDUCIDO", 
                    15: "BOSQUE MESOFILO DE MONTANA", 
                    16: "DESPROVISTO DE VEGETACION", 
                    17: "INDEFINIDO", 
                    18: "MANGLAR", 
                    19: "MATORRAL SUBTROPICAL", 
                    20: "MEZQUITAL", 
                    21: "NUBES", 
                    22: "PASTIZAL CULTIVADO", 
                    23: "PASTIZAL HALOFILO", 
                    24: "PASTIZAL INDUCIDO", 
                    25: "PASTIZAL NATURAL", 
                    26: "PRADERA DE ALTA MONTANA", 
                    27: "SABANOIDE", 
                    28: "SELVA ALTA PERENNIFOLIA", 
                    29: "SELVA ALTA SUBPERENNIFOLIA", 
                    30: "SELVA BAJA CADUCIFOLIA", 
                    31: "SELVA BAJA ESPINOSA CADUCIFOLIA", 
                    32: "SELVA BAJA SUBCADUCIFOLIA", 
                    33: "SELVA DE GALERIA", 
                    34: "SELVA MEDIANA CADUCIFOLIA", 
                    35: "SELVA MEDIANA SUBCADUCIFOLIA", 
                    36: "SELVA MEDIANA SUBPERENNIFOLIA", 
                    37: "SIN VEGETACION APARENTE", 
                    38: "SOMBRAS", 
                    39: "TULAR", 
                    40: "VEGETACION DE DUNAS COSTERAS", 
                    41: "VEGETACION HALOFILA HIDROFILA", 
                    42: "ZONA URBANA"
                }
            basename = get_basename(scene_bundle.get_raster_file())
            all_file = create_filename(directory_helper, '%s_all_features.tif' % basename)
            
            if not is_file(all_file):
                scene_bundle.get_feature_array(all_file)
            
            filename = get_basename(all_file)
            
            
            
            if not is_file(create_filename(directory_helper, '%s.shp' % filename)):
                shell_string = 'docker run --rm -v %s:/data madmex/segment gdal-segment %s.tif -out helper/%s.shp -algo SLIC -region %s' % (directory, filename, filename, region)
                launcher = LocalProcessLauncher()
                LOGGER.debug('Docker command: %s', shell_string)
                launcher.execute(shell_string)
            
            data = read_data_table(create_filename(directory_helper, '%s.shp' % filename))
            
            results = {}
            
            for model_name in models:
                persistence_directory = create_filename(model_directory, model_name)
                print model_name
                model = load_model(model_name)
                model_instance = model.Model(persistence_directory)
                model_instance.load(persistence_directory)
                prediction = model_instance.predict(data)
                results[model_name] = prediction
            print results
            create_directory_path(output)
            write_results(create_filename(directory_helper, '%s.shp' % filename), create_filename(output, '%s_classification.shp' % filename[0:32]), results, categories_dictionaty)
                
        LOGGER.info("--- %s seconds ---" % (time.time() - start_time))   
            