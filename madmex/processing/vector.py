'''
Created on 30/08/2016

@author: erickpalacios
'''
import gdal
def rasterize_vector(target_ds,source_layer, band_list, burn_values):
    '''
    Good reference for rasterizing a vector for an specific attribute:
    http://gis.stackexchange.com/questions/53417/programmatic-raster-vector-calculation?rq=1 
    '''
    if gdal.RasterizeLayer(target_ds, band_list, source_layer, burn_values=burn_values)  != 0:
        raise Exception("error rasterizing layer: %s" % source_layer)
    else:
        return 0
