'''
Created on 15/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

import gdal
from madmex.preprocessing import base
from madmex.preprocessing.bundle import spot5 

def Spot5DN2TOA(indir):
    print "Start folder: ", indir
    bundle = spot5.Bundle(indir)
    if bundle.can_identify():
        #bundle.get_raster()
        bundle.get_sensor()
        #bundle.calculate_toa()
        bundle.export()
    
    

if __name__ == '__main__':
    
    folder = '/Volumes/Imagenes_originales/SPOT5/SPOTMarz/SinNubes/E55542961503031J1A02002/SCENE01'
    #folder = '/Users/erickpalacios/Documents/CONABIO/Tareas/Tarea11/spot5/E55542961503031J1A02002/SCENE01'
    Spot5DN2TOA(folder)
