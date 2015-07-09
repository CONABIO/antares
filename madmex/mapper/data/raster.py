'''
Created on 10/06/2015

@author: erickpalacios
'''
from madmex.mapper.base import BaseData
import gdal, gdalconst
import ogr, osr
from geoalchemy2 import WKTElement

gdal.AllRegister()
gdal.UseExceptions()

class Data(BaseData):
    
    def __init__(self, image_path, gdal_format):
        
        self.image_path = image_path
        self.driver = gdal.GetDriverByName(gdal_format)
            
    def open_file(self, mode = gdalconst.GA_ReadOnly):
        '''
        Open the raster image file with gdal
        '''
        try:
            return gdal.Open(self.image_path, mode)
        except RuntimeError:
            print 'Unable to open raster file %s' % self.image_path
    def extract_metadata(self, data):
        '''
        Extract metadata of the raster image file with gdal functions
        '''
        self.projection = data.GetProjection()
        self.geotransform = data.GetGeoTransform()
        self.dataShape = (data.RasterXSize, data.RasterYSize, data.RasterCount)
        self.footprint = self.get_footprint()
            
    def get_footprint(self):
        '''
        Get the extent of the raster image
        '''
        
        ring = ogr.Geometry(ogr.wkbLinearRing) 
        ring.AddPoint_2D(self.geotransform[0], self.geotransform[3]) 
        ring.AddPoint_2D(self.geotransform[0] + self.geotransform[1] * self.dataShape[0], self.geotransform[3])  
        ring.AddPoint_2D(self.geotransform[0] + self.geotransform[1] * self.dataShape[0], self.geotransform[3] + self.geotransform[5] * self.dataShape[1])  
        ring.AddPoint_2D(self.geotransform[0], self.geotransform[3] + self.geotransform[5] * self.dataShape[1]) 
        ring.CloseRings()
        
        
        sourceSR = osr.SpatialReference()
        sourceSR.ImportFromWkt(self.projection)
        targetSR = osr.SpatialReference() 
        targetSR.ImportFromEPSG(4326)  # Geo WGS84
        coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
        
        footprint = ogr.Geometry(ogr.wkbPolygon)
        footprint.AddGeometry(ring)
        footprint.Transform(coordTrans) 
        wkt = WKTElement(footprint.ExportToWkt(),srid=4326)

        return wkt
        