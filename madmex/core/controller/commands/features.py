'''
Created on Aug 8, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import datetime

import numpy
from sqlalchemy.orm.session import sessionmaker

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.bundle.rapideye import Bundle, _IMAGE
from madmex.mapper.data._gdal import get_geotransform
from madmex.mapper.sensor.rapideye import TILE_ID
from madmex.persistence.database.connection import RapideyeFeatures, ENGINE
from madmex.util import get_parent

NO_VALUE = 0

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
    def handle(self, **options):
        import time
        start_time = time.time()
        
        path = options['path'][0]
        print path
        features_array = []
        
        bundle = Bundle(path)
        
        raster_path = bundle.file_dictionary[_IMAGE]
        
        data_array = open_handle(raster_path)
        data_array = numpy.array(data_array)
        
        print data_array, len(data_array)
        
        print len(data_array[data_array!=0])
        
        for i in range(data_array.shape[0]):
            print 'band: %s' % (i + 1)
            band = data_array[i,:,:].ravel()
            band = band[band!=0]
            features_array.append(numpy.nanpercentile(band,10))
            features_array.append(numpy.nanpercentile(band,25))
            features_array.append(numpy.nanpercentile(band,50))
            features_array.append(numpy.nanpercentile(band,75))
            features_array.append(numpy.nanpercentile(band,90))
            features_array.append(numpy.mean(band))
        geotransform = get_geotransform(raster_path)
        
        features_array.append(geotransform[0])
        features_array.append(geotransform[3])
        
        
        print features_array
        
        
        features_array.append((bundle.get_aquisition_date() - datetime.datetime(1970, 1, 1)).total_seconds())
        tile_id =  bundle.get_sensor().get_attribute(TILE_ID)
        

        features = RapideyeFeatures(band_1_quant_10=features_array[0],
                         band_2_quant_10=features_array[5],
                         band_3_quant_10=features_array[10],
                         band_4_quant_10=features_array[15],
                         band_5_quant_10=features_array[20],
                         band_1_quant_50=features_array[1],
                         band_2_quant_50=features_array[6],
                         band_3_quant_50=features_array[11],
                         band_4_quant_50=features_array[16],
                         band_5_quant_50=features_array[21],
                         band_1_quant_75=features_array[2],
                         band_2_quant_75=features_array[7],
                         band_3_quant_75=features_array[12],
                         band_4_quant_75=features_array[17],
                         band_5_quant_75=features_array[22],
                         band_1_quant_90=features_array[3],
                         band_2_quant_90=features_array[8],
                         band_3_quant_90=features_array[13],
                         band_4_quant_90=features_array[18],
                         band_5_quant_90=features_array[23],
                         band_1_mean=features_array[4],
                         band_2_mean=features_array[9],
                         band_3_mean=features_array[14],
                         band_4_mean=features_array[19],
                         band_5_mean=features_array[24],
                         top=features_array[25],
                         left=features_array[26],
                         time=features_array[27],
                         footprint=tile_id,
                         path=raster_path)
        
        
        klass = sessionmaker(bind=ENGINE, autoflush=False)
        session = klass()
        
        session.add(features)
        session.commit()
        
        print tile_id
        print features_array
        print len(features_array)
        
        print("--- %s seconds ---" % (time.time() - start_time))