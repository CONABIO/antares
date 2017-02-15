'''
madmex.data
'''
import gdal
import numpy
import ogr

from madmex.mapper.data import raster
from madmex.mapper.data._gdal import create_raster_from_reference
from madmex.util import create_file_name


def raster_to_vector():
    pass

def vector_to_raster(vector, output_path, pixel_size, options):
    '''
    This method creates a raster object by burning the values of this
    shape file into a raster with the given resolution.
    '''
    source_layer = vector.get_layer()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    x_resolution = int((x_max - x_min) / pixel_size)
    y_resolution = int((y_max - y_min) / pixel_size)        
    target_ds = gdal.GetDriverByName(str('GTiff')).Create(output_path, x_resolution, y_resolution, 1, gdal.GDT_Int32)
    spatial_reference = vector.get_spatial_reference()         
    target_ds.SetProjection(spatial_reference.ExportToWkt())
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    gdal.RasterizeLayer(target_ds, [1], source_layer, options=options)
    target_ds.FlushCache()
    return raster.Data(output_path)

def raster_to_vector_mask(raster_object, output_path, no_data=[0]):
    raster_array = raster_object.read_data_file_as_array()
    for i in no_data:
        raster_array[raster_array != i] = 0
        
    raster_array[raster_array != 0] = 1
    
    mask_file = create_file_name(output_path, 'mask.tif')
    
    create_raster_from_reference(mask_file, raster_array, raster_object.get_file())
    
    mask_raster = raster.Data(mask_file)
    
    ds = mask_raster._open_file()
    
    rb = ds.GetRasterBand(1)
    
    
    
    dst_layername = 'POLYGONIZED_STUFF'
    drv = ogr.GetDriverByName(str('ESRI Shapefile'))
    dst_ds = drv.CreateDataSource(output_path)
    dst_layer = dst_ds.CreateLayer(dst_layername, srs = None )
    #dst_layer.SetSpatialRef(raster.get_spatial_reference())
    gdal.Polygonize(rb, None, dst_layer, -1, [])
    
    