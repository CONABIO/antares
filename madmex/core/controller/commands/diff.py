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
from madmex.util import check_if_file_exists, remove_file, create_directory_path


#THIS IS A TEST

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
        
        tiles = ["086W_20N","086W_21N","087W_17N","087W_18N","087W_19N","087W_20N","087W_21N","088W_16N","088W_17N","088W_18N","088W_19N","088W_20N","088W_21N","089W_15N","089W_16N","089W_17N","089W_18N","089W_19N","089W_20N","089W_21N","090W_14N","090W_15N","090W_16N","090W_17N","090W_18N","090W_19N","090W_20N","090W_21N","091W_14N","091W_15N","091W_16N","091W_17N","091W_18N","091W_19N","092W_14N","092W_15N","092W_16N","092W_17N","092W_18N","093W_15N","093W_16N","093W_17N","093W_18N","094W_16N","094W_17N","094W_18N","095W_15N","095W_16N","095W_17N","095W_18N","095W_19N","096W_15N","096W_16N","096W_17N","096W_18N","096W_19N","096W_20N","097W_15N","097W_16N","097W_17N","097W_18N","097W_19N","097W_20N","097W_21N","097W_22N","097W_23N","097W_24N","097W_25N","097W_26N","097W_27N","098W_16N","098W_17N","098W_18N","098W_19N","098W_20N","098W_21N","098W_22N","098W_23N","098W_24N","098W_25N","098W_26N","098W_27N","098W_28N","099W_16N","099W_17N","099W_18N","099W_19N","099W_20N","099W_21N","099W_22N","099W_23N","099W_24N","099W_25N","099W_26N","099W_27N","099W_28N","099W_29N","099W_30N","100W_16N","100W_17N","100W_18N","100W_19N","100W_20N","100W_21N","100W_22N","100W_23N","100W_24N","100W_25N","100W_26N","100W_27N","100W_28N","100W_29N","100W_30N","101W_17N","101W_18N","101W_19N","101W_20N","101W_21N","101W_22N","101W_23N","101W_24N","101W_25N","101W_26N","101W_27N","101W_28N","101W_29N","101W_30N","102W_17N","102W_18N","102W_19N","102W_20N","102W_21N","102W_22N","102W_23N","102W_24N","102W_25N","102W_26N","102W_27N","102W_28N","102W_29N","102W_30N","103W_18N","103W_19N","103W_20N","103W_21N","103W_22N","103W_23N","103W_24N","103W_25N","103W_26N","103W_27N","103W_28N","103W_29N","103W_30N","103W_31N","104W_18N","104W_19N","104W_20N","104W_21N","104W_22N","104W_23N","104W_24N","104W_25N","104W_26N","104W_27N","104W_28N","104W_29N","104W_30N","104W_31N","105W_19N","105W_20N","105W_21N","105W_22N","105W_23N","105W_24N","105W_25N","105W_26N","105W_27N","105W_28N","105W_29N","105W_30N","105W_31N","105W_32N","106W_21N","106W_22N","106W_23N","106W_24N","106W_25N","106W_26N","106W_27N","106W_28N","106W_29N","106W_30N","106W_31N","106W_32N","107W_23N","107W_24N","107W_25N","107W_26N","107W_27N","107W_28N","107W_29N","107W_30N","107W_31N","107W_32N","108W_24N","108W_25N","108W_26N","108W_27N","108W_28N","108W_29N","108W_30N","108W_31N","108W_32N","109W_22N","109W_23N","109W_24N","109W_25N","109W_26N","109W_27N","109W_28N","109W_29N","109W_30N","109W_31N","109W_32N","110W_22N","110W_23N","110W_24N","110W_25N","110W_27N","110W_28N","110W_29N","110W_30N","110W_31N","110W_32N","111W_24N","111W_25N","111W_26N","111W_27N","111W_28N","111W_29N","111W_30N","111W_31N","111W_32N","112W_24N","112W_25N","112W_26N","112W_27N","112W_28N","112W_29N","112W_30N","112W_31N","112W_32N","113W_26N","113W_27N","113W_28N","113W_29N","113W_30N","113W_31N","113W_32N","113W_33N","114W_26N","114W_27N","114W_28N","114W_29N","114W_30N","114W_31N","114W_32N","114W_33N","115W_27N","115W_28N","115W_29N","115W_30N","115W_31N","115W_32N","115W_33N","116W_30N","116W_31N","116W_32N","116W_33N","117W_32N","117W_33N"]
        
        print len(tiles)
        
        path_1985 = '/Users/agutierrez/Dropbox/Multivariado/classification/classification_1985.tif'
        path_2009 = '/Users/agutierrez/Dropbox/Multivariado/classification/classification_2009.tif'
        path_change = '/Users/agutierrez/Dropbox/Multivariado/change.tif'
        
        
        path_change_1985 = '/Users/agutierrez/Dropbox/Multivariado/classification/change_1985.tif'
        path_change_2009 = '/Users/agutierrez/Dropbox/Multivariado/classification/change_2009.tif'
        
        gdal_format = 'GTiff'
        
        
        image_1985 = raster.Data(path_1985, gdal_format)
        image_2009 = raster.Data(path_2009, gdal_format)
        image_change = raster.Data(path_change, gdal_format)
                
        array_1985 = image_1985.read_data_file_as_array()
        array_2009 = image_2009.read_data_file_as_array()
        array_change = image_change.read_data_file_as_array()
                
        print array_1985.shape
        print array_2009.shape
        print numpy.unique(array_1985, return_counts=True)[0]
        print numpy.unique(array_1985, return_counts=True)[1] * 30 * 30 * 0.0001
        
        
        
        print numpy.unique(array_1985[array_change > .5], return_counts=True)
        print numpy.unique(array_2009[array_change > .5], return_counts=True)
        
        
        array_1985_masked = array_1985[array_change > .5]
        array_2009_masked = array_2009[array_change > .5]
        
        counts ={'1.0->2.0':0,
                 '1.0->3.0':0,
                 '1.0->4.0':0,
                 '1.0->5.0':0,
                 '2.0->1.0':0,
                 '2.0->3.0':0,
                 '2.0->4.0':0,
                 '2.0->5.0':0,
                 '3.0->1.0':0,
                 '3.0->2.0':0,
                 '3.0->4.0':0,
                 '3.0->5.0':0,
                 '4.0->1.0':0,
                 '4.0->2.0':0,
                 '4.0->3.0':0,
                 '4.0->5.0':0,
                 '5.0->1.0':0,
                 '5.0->2.0':0,
                 '5.0->3.0':0,
                 '5.0->4.0':0}

        
        
        for i in range(len(array_1985_masked)):
            if not array_1985_masked[i] == array_2009_masked[i]:
                counts['%s->%s' % (array_1985_masked[i], array_2009_masked[i])] = counts['%s->%s' % (array_1985_masked[i], array_2009_masked[i])] + 30 * 30 * 0.0001
                
        import json
        print json.dumps(counts, indent=1)
        
        
        array_1985[array_change < .5] = 0
        array_2009[array_change < .5] = 0
        
        
        create_raster_from_reference(path_change_1985, array_1985, path_1985, data_type=gdal.GDT_Byte)
        create_raster_from_reference(path_change_2009, array_2009, path_1985, data_type=gdal.GDT_Byte)
        
        
        
        
        '''
        init = 1985
        gdal_format = 'GTiff'
        for tile in tiles:
            for i in range(30):
                path_a = '/LUSTRE/MADMEX/tasks/2016_tasks/matt_hansen_forests/tiles/%s/%s_%s.tif' % (tile, tile, init+i)
                path_b = '/LUSTRE/MADMEX/tasks/2016_tasks/matt_hansen_forests/tiles/%s/%s_%s.tif' % (tile, tile, init+i+1)
                path_c = '/LUSTRE/MADMEX/tasks/2016_tasks/matt_hansen_forests/tiles_example/%s/%s_%s_%s.tif' % (tile, tile, init+i,init+i+1)
                directory = '/LUSTRE/MADMEX/tasks/2016_tasks/matt_hansen_forests/tiles_example/%s/' % tile
                
                print path_a
                print path_b
                print path_c
                
                #remove_file(path_c)
                create_directory_path(directory)
                
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
                    
                    upper = 30  
                    lower = 10                 
                    
                    diff[(array_b < lower) & (array_a > upper)] = 1
                    diff[(array_b > upper) & (array_a < lower)] = 2
                    
                    #diff[mask] = -9999
        
                
                
                    create_raster_from_reference(path_c, diff, path_a, data_type=gdal.GDT_Byte)
                else:
                    print 'File exists.'
                
                print 'Done %s-%s' % (init+i,init+i)    
        
        '''
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
        