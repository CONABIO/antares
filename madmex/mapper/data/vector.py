'''
Created on 10/06/2015

@author: erickpalacios
'''
from madmex.mapper.base import BaseData
import osr, ogr
import gdal
from geoalchemy2 import WKTElement

gdal.AllRegister()
ogr.UseExceptions()


class Data(BaseData):
    
    def __init__(self, image_path, ogr_format):
        
        self.image_path = image_path
        try:
            self.driver = ogr.GetDriverByName(ogr_format)
        except AttributeError:
            print 'Cannot access driver for format %s' % ogr_format
    def open_file(self):
        '''
        Open the vector image file with ogr
        '''
        try:
            return self.driver.Open(self.image_path, 0) # 0 means read-only. 1 means writeable.
        except Exception:
            print 'Unable to open shape file %s' % self.image_path
            
    def extract_metadata(self, data):
        '''
        Extract metadata of the vector image file with ogr functions
        '''
        self.layer = data.GetLayer()
        self.footprint = self.get_footprint()
        
        
    def get_footprint(self):
        '''
        Get the extent of the raster image
        '''
        extent = self.layer.GetExtent()
        
        ring = ogr.Geometry(ogr.wkbLinearRing) 
        ring.AddPoint_2D(extent[0],extent[2])
        ring.AddPoint_2D(extent[1], extent[2])
        ring.AddPoint_2D(extent[1], extent[3])
        ring.AddPoint_2D(extent[0], extent[3])
        ring.CloseRings()

        
        
        sourceSR = self.layer.GetSpatialRef()
        targetSR = osr.SpatialReference() 
        targetSR.ImportFromEPSG(4326)  # Geo WGS84
        coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
        
        footprint = ogr.Geometry(ogr.wkbPolygon)
        footprint.AddGeometry(ring)
        footprint.Transform(coordTrans) 
        wkt = WKTElement(footprint.ExportToWkt(),srid=4326)
        return wkt
        