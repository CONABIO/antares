'''
Created on 10/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals
import logging
import gdal
import ogr
from madmex.mapper.base import BaseData
import osr


gdal.AllRegister()
ogr.UseExceptions()
LOGGER = logging.getLogger(__name__)
ESRI_FORMAT = 'ESRI Shapefile'
def create_empty_layer(filename, layer_name, projection_reference = None, geom_type=ogr.wkbPolygon, options = []):
    driver = ogr.GetDriverByName(str(ESRI_FORMAT))
    spatial_reference = osr.SpatialReference()
    if not projection_reference:
        spatial_reference.ImportFromEPSG(4326) # Geo WGS84)
        srid = spatial_reference.GetAuthorityCode(None)
    else:
        spatial_reference.ImportFromWkt(projection_reference)
        spatial_reference.AutoIdentifyEPSG()
        srid = spatial_reference.GetAuthorityCode(None)
    data_source = driver.CreateDataSource(filename)
    data_layer = data_source.CreateLayer(layer_name, spatial_reference,  geom_type)
    return (data_layer, data_source) #we have to return the data source for avoiding segmentation fault in the calling function

class Data(BaseData):
    '''
    This class represents a vector type file.
    '''
    def __init__(self, image_path, ogr_format):
        super(Data, self).__init__()
        self.image_path = image_path.encode('utf-8')
        self.footprint = None
        self.layer = None
        try:
            ogr_format = ogr_format.encode('utf-8')
            self.driver = ogr.GetDriverByName(ogr_format)
        except AttributeError:
            LOGGER.error('Cannot access driver for format %s', ogr_format)
        self.data_file = self._open_file()
        if self.data_file is None:
            LOGGER.info('Unable to open file: %s' % self.image_path)
        else:
            LOGGER.info('Extracting metadata: footprint and layer of %s' % self.image_path)
            self._extract_metadata()
        
    def _open_file(self):
        '''
        Open the vector image file with ogr.
        '''
        try:
            LOGGER.debug('Open vector file: %s' % self.image_path)
            return self.driver.Open(self.image_path, 0)  # 0 means read-only. 1 means writeable.
        except Exception:
            LOGGER.error('Unable to open shape file: %s', self.image_path)
    def _extract_metadata(self):
        '''
        Extract metadata from the raster image file using gdal functions.
        '''
        if  self.layer is None:
            self.layer = self.data_file.GetLayer()
        if self.footprint is None:
            self.footprint = self._get_footprint()
        self.srs = self.layer.GetSpatialRef()
        self.srs.AutoIdentifyEPSG() #This is the equivalent of get projection of data source object of gdal 
        self.srid = self.srs.GetAuthorityCode(None)
    def _get_footprint(self):
        '''
        Returns the extent of the shape image.
        '''
        self.extent = self.layer.GetExtent()
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint_2D(self.extent[0], self.extent[2])
        ring.AddPoint_2D(self.extent[1], self.extent[2])
        ring.AddPoint_2D(self.extent[1], self.extent[3])
        ring.AddPoint_2D(self.extent[0], self.extent[3])
        ring.CloseRings()
        spacial_reference = self.layer.GetSpatialRef()
        return self._footprint_helper(ring, spacial_reference)
    
if __name__ == '__main__':
    image = '/Users/erickpalacios/Documents/CONABIO/MADMEXdata/eodata/footprints/country_mexico/country_mexico_2012.shp'
    image = '/Users/erickpalacios/Documents/CONABIO/Tareas/Redisenio_MADMEX/clasificacion_landsat/landsat8/classification/NDVImetrics_3_02_08.tif.shp'
    FORMAT =  'ESRI Shapefile'
    data_class = Data(image, FORMAT)
    print data_class.layer
    print data_class.footprint
    print data_class.layer.GetName()
    print data_class.layer.GetLayerDefn()
    print data_class.layer.GetLayerDefn().GetFieldCount()
    print osr.SpatialReference()
    srs = osr.SpatialReference()
    print srs.ImportFromEPSG(4326) 
    print srs.GetAuthorityCode(None)
    print 'srid'
    print data_class.srid
    print 'get spatial reference'
    print data_class.layer.GetSpatialRef()
    print 'srs'
    print data_class.srs
    print 'projection defined'
    projection = 'PROJCS["UTM Zone 15, Northern Hemisphere",GEOGCS["Unknown datum based upon the WGS 84 ellipsoid",DATUM["Not specified (based on WGS 84 spheroid)",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-93],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
    print osr.SpatialReference()
    srs = osr.SpatialReference()
    print srs.ImportFromWkt(projection)
    print srs.AutoIdentifyEPSG()
    print srs.GetAuthorityCode(None)
    print srs.ImportFromEPSG(4326)
    
