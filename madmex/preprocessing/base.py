'''
Created on 16/07/2015

@author: erickpalacios
'''

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
def calculate_rad_ref(data, gain, offset, imaging_date, sun_elevation):
    rad = calc_spot_rad(data.astype(np.float), gain, offset)
    sun_distance = calc_distance_Sun_Earth(str(imaging_date))
    return calc_spot5_toa(rad, sun_distance, sun_elevation)