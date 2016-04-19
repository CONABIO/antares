'''
Created on 19/04/2016

@author: erickpalacios
'''
import numpy
import numexpr

def calculate_ndvi(band4, band3, mode=numpy.int16):
    '''
    Calculate the normalized differenced vegetation index of a raster image
    '''
    spectralindex = numexpr.evaluate("100 * (1.*(band4 - band3) / (band4 + band3))")
    spectralindex[numpy.where(band4 - band3 == 0)] = 0
    spectralindex[numpy.where(numpy.logical_and(band4 == 0, band3 == 0))] = None
    return spectralindex.astype(mode)