'''
Created on 10/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

import logging

import gdal
import ogr
import osr
import pandas

from madmex.mapper.base import BaseData
from madmex.util import create_file_name, is_directory, create_directory_path, \
    is_file, get_base_name


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

def create_shape_from_json(id, json, output_directory):
    '''
    Given a json string containing coordinates, this method creates a shape file.
    '''
    create_directory_path(output_directory)
    filename = create_file_name(output_directory, '%s.shp' % id)
    shape = Data(filename)
    if is_file(filename):
        shape.driver.DeleteDataSource(filename)
    data_source = shape.driver.CreateDataSource(filename)
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromEPSG(4326)    
    layer = data_source.CreateLayer(str('layer'), spatial_reference, geom_type=ogr.wkbPolygon)
    layer.CreateField(ogr.FieldDefn(str('id'), ogr.OFTString))
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetField(str('id'), str(id))
    geometry = ogr.CreateGeometryFromJson(str(json))
    feature.SetGeometry(geometry)
    layer.CreateFeature(feature)
    shape.close()
    return shape
class Data(BaseData):
    '''
    This class represents a vector type file.
    '''
    def __init__(self, image_path, ogr_format=str('ESRI Shapefile')):
        super(Data, self).__init__()
        self.image_path = image_path.encode('utf-8')
        self.footprint = None
        self.layer = None
        self._open_object = None
        try:
            ogr_format = ogr_format.encode('utf-8')
            self.driver = ogr.GetDriverByName(ogr_format)
        except AttributeError:
            LOGGER.error('Cannot access driver for format %s', ogr_format)
        #self.data_file = self._open_file()
        #if self.data_file is None:
        #    LOGGER.info('Unable to open file: %s' % self.image_path)
        #else:
        #    LOGGER.info('Extracting metadata: footprint and layer of %s' % self.image_path)
        #    self._extract_metadata()
        
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
        self.extent = self.get_layer().GetExtent()
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint_2D(self.extent[0], self.extent[2])
        ring.AddPoint_2D(self.extent[1], self.extent[2])
        ring.AddPoint_2D(self.extent[1], self.extent[3])
        ring.AddPoint_2D(self.extent[0], self.extent[3])
        ring.CloseRings()
        spacial_reference = self.get_layer().GetSpatialRef()
        return self._footprint_helper(ring, spacial_reference)
    def open(self, writable=0):
        '''
        This method loads the the shape that this object represents in memory.
        '''
        if not self._open_object:
            LOGGER.debug('Opening the shape file.')
            self._open_object = self.driver.Open(self.image_path, writable)
        return self._open_object
    def close(self):
        '''
        This method deallocates the memory that the shape file represents.
        '''
        self._open_object = None
    def get_layer(self):
        '''
        This method returns the layer for this shape file.
        '''
        return self.open().GetLayer()
    def get_spatial_reference(self):
        '''
        This method returns the spatial referecne of this shape.
        '''
        layer = self.get_layer()
        spatial_reference = layer.GetSpatialRef()
        print spatial_reference
        return spatial_reference
    
    def split(self, output_directory, column=0):
        '''
        This method will take a input shape and iterate over its features, creating
        a new shape file with each one of them. It copies all the fields and the
        same spatial reference from the original file. The created files are saved
        in the destination directory using the number of the field given. 
        '''
        layer = self.get_layer()
        layer_name = layer.GetName()
        spatial_reference = layer.GetSpatialRef()
        in_feature = layer.GetNextFeature()
        layer_definition = layer.GetLayerDefn()
        field_definition = layer_definition.GetFieldDefn(0)
        column_name = field_definition.GetName() 
        shape_files = []
        create_directory_path(output_directory)
        in_layer_definition = layer.GetLayerDefn()
        while in_feature:            
            in_feature_name = in_feature.GetField(column_name)
            output_name = create_file_name(output_directory, '%s.shp' % in_feature_name)
            shape_files.append(output_name)
            if is_file(output_name):
                self.driver.DeleteDataSource(output_name)
            data_source = self.driver.CreateDataSource(output_name)
            out_layer = data_source.CreateLayer(layer_name, spatial_reference, geom_type=ogr.wkbPolygon)
            for i in range(0, in_layer_definition.GetFieldCount()):
                fieldDefn = in_layer_definition.GetFieldDefn(i)
                out_layer.CreateField(fieldDefn)
            outLayerDefn = out_layer.GetLayerDefn()
            geometry = in_feature.GetGeometryRef()
            out_feature = ogr.Feature(outLayerDefn)
            out_feature.SetGeometry(geometry)
            for i in range(0, outLayerDefn.GetFieldCount()):
                out_feature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), in_feature.GetField(i))
            out_layer.CreateFeature(out_feature)
            
            out_feature = None
            in_feature = None
            in_feature = layer.GetNextFeature()
        self.close()
        return [Data(filename) for filename in shape_files]
    def to_dataframe(self):
        layer = self.get_layer()
        layer_definition = layer.GetLayerDefn()
        dataframe = {}
        in_feature = layer.GetNextFeature()
        for i in range(0, layer_definition.GetFieldCount()):
            field_definition = layer_definition.GetFieldDefn(i)
            column_name = field_definition.GetName()
            dataframe[column_name] = []
        
        while in_feature:
            for i in range(0, layer_definition.GetFieldCount()):
                field_definition = layer_definition.GetFieldDefn(i)
                column_name = field_definition.GetName()
                dataframe[column_name].append(in_feature.GetField(i))
            in_feature = layer.GetNextFeature()
        return pandas.DataFrame(dataframe)
        

    def intersect(self, output_directory, geometry):
        layer = self.get_layer()
        layer_name = layer.GetName()
        spatial_reference = layer.GetSpatialRef()
        
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(4326)
        
        
        coordTransform = osr.CoordinateTransformation(inSpatialRef, spatial_reference)
    
        geometry.Transform(coordTransform)
                
        in_feature = layer.GetNextFeature()
        layer_definition = layer.GetLayerDefn()
        field_definition = layer_definition.GetFieldDefn(0)
        column_name = field_definition.GetName() 
        shape_files = []
        create_directory_path(output_directory)
        in_layer_definition = layer.GetLayerDefn()
        output_name = output_directory       
        print output_name
        if is_file(output_name):
            self.driver.DeleteDataSource(output_name)
        data_source = self.driver.CreateDataSource(output_name)
        out_layer = data_source.CreateLayer(layer_name, spatial_reference, geom_type=ogr.wkbPolygon)
        for i in range(0, in_layer_definition.GetFieldCount()):
            fieldDefn = in_layer_definition.GetFieldDefn(i)
            out_layer.CreateField(fieldDefn)
        while in_feature:            
            outLayerDefn = out_layer.GetLayerDefn()
            feature_geometry = in_feature.GetGeometryRef()
            out_feature = ogr.Feature(outLayerDefn)            
            
            print geometry.ExportToWkt()
            print feature_geometry.ExportToWkt()
            if geometry.Intersect(feature_geometry):
                print 'It intersects!!!!'
                intersection = geometry.Intersection(feature_geometry)
                out_feature.SetGeometry(intersection)
                for i in range(0, outLayerDefn.GetFieldCount()):
                    out_feature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), in_feature.GetField(i))
                out_layer.CreateFeature(out_feature)
            out_feature = None
            in_feature = None
            in_feature = layer.GetNextFeature()
        self.close()
        return Data(output_name)

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
    
