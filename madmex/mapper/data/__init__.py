'''
madmex.data
'''
import gdal
import numpy

from madmex.mapper.data import raster


def raster_to_vector():
    pass

def vector_to_raster(vector, output_path, pixel_size):
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
    gdal.RasterizeLayer(target_ds, [1], source_layer, options = ["ATTRIBUTE=OBJECTID"])
    target_ds.FlushCache()
    return raster.Data(output_path)
