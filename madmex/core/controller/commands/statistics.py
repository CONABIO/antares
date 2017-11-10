'''
Created on Jan 19, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import json
import logging
import math

import gdal
import numpy
from numpy.f2py.rules import aux_rules
from scipy.constants.constants import hectare

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands import get_bundle_from_path
from madmex.core.controller.commands.aggregate import INITIAL_ARRAY
from madmex.util import get_basename, get_parent, create_filename

LOGGER = logging.getLogger(__name__)
BUNDLE_PACKAGE = 'madmex.mapper.bundle'

INITIAL_ARRAY = {'Bosque de Coniferas de Oyamel Ayarin Cedro' : [1],
                 'Bosque de Coniferas de Pino y Tascate' : [3],
                 'Bosque de Encino y Bosque de Galeria' : [2],
                 'Chaparral' : [6],
                 'Mezquital y Submontano' : [4],
                 'Bosque Cultivado e Inducido' : [123],
                 'Selva Baja Perennifolia y Bosque Mesofilo' : [8],
                 'Selva Baja y Mediana Subperennifolia Galeria y Palmar Natural' : [10],
                 'Manglar y Peten' : [16],
                 'Selva Mediana y Alta Perennifolia' : [12],
                 'Selva Alta Subperennifolia' : [11],
                 'Selva Baja Caducifolia Subcaducifolia y Matorral Subtropical' : [9],
                 'Selva Mediana Caducifolia y Subcaducifolia' : [13],
                 'Mezquital Xerofilo Galeria y Desertico Microfilo' : [5],
                 'Matorral Crasicaule' : [7],
                 'Matorral Espinoso Tamaulipeco' : [22],
                 'Matorral Sarco-Crasicaule' : [17],
                 'Matorral Sarcocaule' : [19],
                 'Matorral Sarco-Crasicaule de Neblina' : [18],
                 'Matorral Rosetofilo Costero' : [23],
                 'Matorral Desertico Rosetofilo' : [21],
                 'Popal' : [15],
                 'Tular' : [14],
                 'Vegetacion de Dunas Costeras' : [20],
                 'Vegetacion de Desiertos Arenosos' : [24],
                 'Vegetacion Halofila Hidrofila' : [25],
                 'Vegetacion Halofila Xerofila y Gipsofila' : [26],
                 'Pastizales' : [27],
                 'Tierras Agricolas' : [28],
                 'Urbano y Construido' : [31],
                 'Suelo Desnudo' : [30],
                 'Agua' : [29],
                 'Sombras' : [98],
                 'Nubes' : [99]}

def _get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    return get_bundle_from_path(path, '../../../mapper', BUNDLE_PACKAGE)
class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        This command defines only an additional argument. The user must provide
        a path to ingest, if several paths are given, all of the folders will
        be ingested.
        '''
        parser.add_argument('--path', nargs='*')
        parser.add_argument('--target', nargs='*')

    def handle(self, **options):
        '''
        This is the code that does the ingestion.
        '''
        interest_band = 1
        for image_path in options['path']:
                print image_path
                ds = gdal.Open(image_path)
                bands = ds.RasterCount           
                geotransform = ds.GetGeoTransform()     
                x_resolution = geotransform[1]
                y_resolution = geotransform[5]
                pixel_area = abs(x_resolution * y_resolution)                
                array = numpy.array(ds.GetRasterBand(interest_band).ReadAsArray())
                print numpy.unique(array)
                flat = numpy.ravel(array)
                length = len(flat)
                parent = get_parent(image_path)
                basename = '%s.txt' % get_basename(image_path)
                target = create_filename(parent, basename)
                count = 1                
                values = {}
                progress = 0
                for value in flat:
                    count = count + 1
                    if not values.get(value):
                        values[value] = 1
                    else:
                        values[value] = values[value] + 1
                    if count % 1000000 == 0:    
                        aux = progress
                        progress = math.floor(100 * count / float(length))
                        if not aux == progress:
                            print  str(int(progress)) + '%\r'
                added = self.add_up(INITIAL_ARRAY, values)
                area = self.transform_to_area(added, pixel_area)
                with open(target, "a") as f:
                    json.dump(area, f)

    def print_dict(self, values):
        for key in values.keys():
            if not key == 0:
                print '%s : %s' % (key, values.get(key))

    def sum_no_zero(self, values):
        total = 0
        for key in values.keys():
            if not key == 0:
                total = total + values.get(key)
        print total        
        for key in values.keys():
            if not key == 0:
                print values.get(key) * 100 / float(total)

    def add_up(self, classifications, values):
        result = {}
        for classfification in classifications.keys():
            counter = 0
            for key in values.keys():
                if key in classifications.get(classfification):
                    counter = counter + values.get(key)
                    
            result[classfification] = counter
        return result

    def transform_to_area(self, values, area_in_pixel):
        result = {}
        for key in values.keys():
            result[key] = values.get(key) * area_in_pixel / hectare
        return result
