'''
Created on 19/04/2016

@author: erickpalacios
'''
import numpy
import numexpr

def calculate_ndvi(band4, band3, mode=numpy.int16):
    '''
    Calculate the normalized differenced vegetation index of a raster image
    Returns an image of two bands
    '''
    spectralindex = numexpr.evaluate("100 * (1.*(band4 - band3) / (band4 + band3))")
    spectralindex[numpy.where(band4 - band3 == 0)] = 0
    spectralindex[numpy.where(numpy.logical_and(band4 == 0, band3 == 0))] = None
    return spectralindex.astype(mode)

def calculate_index(band_a, band_b, mode=numpy.int16):
    '''
    Calculate the normalized differenced vegetation index of a raster image
    Returns an image of two bands
    '''
    spectralindex = numexpr.evaluate("100 * (1.*(band_a - band_b) / (band_a + band_b))")
    spectralindex[numpy.where(band_a - band_b == 0)] = 0
    spectralindex[numpy.where(numpy.logical_and(band_a == -9999, band_b == -9999))] = -9999
    return spectralindex.astype(mode)
