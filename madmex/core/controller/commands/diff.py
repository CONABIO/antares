'''
Created on Jun 25, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

import gdal
import numpy

from madmex import _
from madmex.core.controller.base import BaseCommand
from madmex.mapper.data import raster, vector, vector_to_raster
from madmex.mapper.data._gdal import create_raster_from_reference
from madmex.util import check_if_file_exists, remove_file


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--a', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--b', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        sum_of_numbers = 0
        #path_a = options['a'][0]
        #path_b = options['b'][0]
        
        init = 1985
        gdal_format = 'GTiff'
        for i in range(30):
            path_a = '/LUSTRE/MADMEX/tasks/2016_tasks/matt_hansen_forests/final/Mexico_TCC_%s.vrt' % (init+i)
            path_b = '/LUSTRE/MADMEX/tasks/2016_tasks/matt_hansen_forests/final/Mexico_TCC_%s.vrt' % (init+i+1)
            path_c = '/LUSTRE/MADMEX/tasks/2017_tasks/conafor_entrega_junio/tcc/Mexico_TCC_%s_%s.tif' % (init+i,init+i+1)
            
            print path_a
            print path_b
            print path_c
            
            #remove_file(path_c)
            
            if not check_if_file_exists(path_c):
            
                image_a = raster.Data(path_a, gdal_format)
                image_b = raster.Data(path_b, gdal_format)
            
                array_a = image_a.read_data_file_as_array()
                array_b = image_b.read_data_file_as_array()
            
                #mask = ((array_a < 30) | (70 < array_a)) & ((array_b < 30) | (70 < array_b))
                
                #array_a[array_a <= 30] = 0
                #array_a[30 < array_a] = 1
                
                #array_b[array_b <= 30] = 0
                #array_b[30 < array_b] = 1 
                
                #diff = array_b - array_a  
                
                
                diff = numpy.zeros(numpy.shape(array_a))                     
                
                diff[((array_b - array_a) < 10) & (array_a >= 30)] = 1
                
                #diff[mask] = -9999
            
                '''
                absolute = numpy.absolute(diff)
                absolute[absolute < 30] = 0
                absolute[absolute != 0] = 1
                absolute[diff < 0] *= 2
                '''
            
                create_raster_from_reference(path_c, diff, path_a, data_type=gdal.GDT_Int16)
            else:
                print 'File exists.'
            
            print 'Done %s-%s' % (init+i,init+i)
        '''
        
        total = {}
        for state in ['Campeche','Chiapas','Oaxaca','Quintana_Roo','Yucatan']:
            total_state = {}
            for where in ['anps', 'corr-anp', 'est-corr-anp']:
                raster_path = '/LUSTRE/MADMEX/staging/2017_tasks/corredor_biologico/analisis_por_estado-vegetacion/shapes_area_interes_por_estado/%s/%s_%s.tif' % (state, state, where)
                
                print raster_path
                
                image = raster.Data(raster_path, gdal_format)
                array = image.read_data_file_as_array()
                array[array > 0] = 1
                counts = numpy.unique(array, return_counts=True)
                print counts
                total_state[where] = counts[1][1]
            total[state] = total_state

        print total
        
        
        
        init = 1985
        
        
        
        
        for state in ['Campeche','Chiapas','Oaxaca','Quintana_Roo','Yucatan']:
            statistics_by_state = []
            for where in ['anps', 'corr-anp', 'est-corr-anp']:
                for i in range(30):
                    
                    mask_path = '/LUSTRE/MADMEX/staging/2017_tasks/corredor_biologico/analisis_por_estado-vegetacion/shapes_area_interes_por_estado/%s/%s_%s.tif' % (state, state, where)
                    mask_image = raster.Data(mask_path, gdal_format)
                    mask_array = mask_image.read_data_file_as_array()
                
                    
                    
                    
        
                    path_c = '/LUSTRE/MADMEX/staging/2017_tasks/corredor_biologico/analisis_por_estado-vegetacion/corte_por_area_interes_en_estado/diff-michael-repro/Mexico_TCC_%s_%s_%s_%s.tif' % (state, init+i,init+i+1,where)
                    
                    print path_c
                    
                    image_c = raster.Data(path_c, gdal_format)
                    
                    array_c = image_c.read_data_file_as_array()
                    #array_c = array_c[array_c > -9999]
                    
                    counts = numpy.unique(array_c, return_counts=True)
                    print counts
                    
                    
                    #size_non_zero = len(array_c)
                    #final = numpy.zeros(size_non_zero, dtype=numpy.int)
                    #final[(-40 < array_c) & (array_c < 40)] = 0
                    #final[40 < array_c] = 1
                    #final[array_c < -40] = 2
                    
                    
                    x_resolution = image_c.get_geotransform()[1]
                    y_resolution = image_c.get_geotransform()[5]
                    
                    area = x_resolution * y_resolution
                    
                
                    stats = {}
                    
                    stats['period'] = '%s-%s' % (init+i,init+i+1)
                    stats['type'] = where
                    stats['resolution'] = area
                    
                    if len(counts[1]) > 2:
                        stats['negative'] = counts[1][0]
                        stats['no-change'] = counts[1][1]
                        stats['positive'] = counts[1][2]
                    else:
                        stats['negative'] = 0
                        stats['no-change'] = counts[1][0]
                        stats['positive'] = 0
                     
                    #stats['net'] = (counts[1][1] - counts[1][2])
                    stats['total'] = total[state][where]
                    statistics_by_state.append(stats)
                    print statistics_by_state
            
            stats_path = '/LUSTRE/MADMEX/staging/2017_tasks/corredor_biologico/analisis_por_estado-vegetacion/shapes_area_interes_por_estado/stats/estadisticas-michael-repro-%s.json' % state
            
            import json
            with open(stats_path, 'w') as outfile:
                json.dump(statistics_by_state, outfile)
        
        '''
        