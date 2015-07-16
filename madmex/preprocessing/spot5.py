'''
Created on 15/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

import gdal

from madmex.mapper.bundle.spot5 import Bundle
import numpy as np


def calc_spot_rad(data,gain,offset):
    b = 0
    rad = data
    for g in gain:
        rad[b,:,:] = data[b,:,:]/g+offset[b]
        b = b+1
        
    return rad

def calc_spot5_toa(rad, sun_distance, sun_elevation):
    E = [1843,1568,1052,233]
    BANDS = 4
    toa = rad
    for i in range(BANDS):
        toa[i,:,:] = (np.pi*rad[i,:,:]*sun_distance)/(E[i]*np.cos(sun_elevation))
        
    return toa

def calc_distance_Sun_Earth(datestr):
    """
    returns distance between sun and earth in AU for a given date. Date needs to be a string using format YYYY-MM-DD or datetime object from metadata
    """
    import datetime
    import ephem
    sun = ephem.Sun()   # @UndefinedVariable
    if isinstance(datestr, str):
        sun.compute(datetime.datetime.strptime(datestr, '%Y-%m-%d').date())
    elif isinstance(datestr, datetime.datetime ):
        sun.compute(datestr)
    sun_distance = sun.earth_distance  # needs to be between 0.9832898912 AU and 1.0167103335 AU
    
    return sun_distance


    
    
def gdal_error_handler(err_class, err_num, err_msg):
    errtype = {
        gdal.CE_None:'None',
        gdal.CE_Debug:'Debug',
        gdal.CE_Warning:'Warning',
        gdal.CE_Failure:'Failure',
        gdal.CE_Fatal:'Fatal'
    }
    err_msg = err_msg.replace('\n',' ')
    err_class = errtype.get(err_class, 'None')
    print 'Error Number: %s' % (err_num)
    print 'Error Type: %s' % (err_class)
    print 'Error Message: %s' % (err_msg)
    
    
def Spot5DN2TOA(indir):
    print "Start folder: "
    bundle = Bundle(indir)
    print bundle.can_identify()

if __name__ == '__main__':
    
    # install error handler
    gdal.PushErrorHandler(gdal_error_handler)
    folder = '/Volumes/Imagenes_originales/SPOT5/SPOTMarz/SinNubes/E55542961503031J1A02002/SCENE01'
    Spot5DN2TOA(folder)
    gdal.PopErrorHandler()
