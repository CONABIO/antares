'''
Created on Jun 3, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from __builtin__ import getattr
import os
import unittest

from madmex.configuration import SETTINGS
from madmex.core import controller
from madmex.mapper.base import _get_attribute
from madmex.util import get_last_package_from_name, create_directory_path,\
    get_parent

class Test(unittest.TestCase):

    def test_get_last_package_from_name(self):
        self.assertEqual(get_last_package_from_name('name.for.package'), 'package')

    def test_copyright(self):
        """
        Pulls copyright string and checks format is correct.
        """
        self.assertRegexpMatches(controller.madmex_copyright(), r"MADMex \d{4}-\d{4}")

    def test_configuration(self):
        """
        Creates a new configuration file loads it and tests if a setting is
        loaded correctly.
        """
        key = 'testing'
        value = 'setting'
        path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'test.ini'
        )
        
        test_file = open(path, 'w+')
        test_file.write('[madmex]\n')
        test_file.write('%s=%s\n' % (key, value))
        test_file.close()
        
        from madmex.configuration import ENVIRONMENT_VARIABLE
        SETTINGS.reload()
        os.environ[ENVIRONMENT_VARIABLE] = path
        SETTINGS.reload()
        self.assertEqual(value, getattr(SETTINGS, key.upper()))
        del os.environ[ENVIRONMENT_VARIABLE]
        os.remove(path)
    def test_get_attribute(self):
        '''
        Tests the get attribute function. This tries several scenarios.
        '''
        dictionary = {'1': {'2': {'3': '4'}, '5': {'6': '7'}, '8': {'9': '0'}}}
    
        self.assertEqual(_get_attribute(['1','5','6'], dictionary), '7')
        self.assertEqual(_get_attribute(['1','2','3'], dictionary), '4')
        self.assertEqual(_get_attribute(['9','NoneSense'], dictionary), None)
        self.assertEqual(_get_attribute([], dictionary), None)
        self.assertEqual(_get_attribute(None, dictionary), None)
        self.assertEqual(_get_attribute(123, dictionary), None)

    def test_landsat_parser(self):
        '''
        Test for the landsat parser, creates a parser instance pointing to a
        landsat xml file and then two properties are retrieved.
        '''
        import madmex.mapper.parser.landsat as landsat
        metadata = "/LUSTRE/MADMEX/eodata/etm+/25046/2013/2013-04-03/l1t/LE70250462013093ASN00_MTL.txt"
        parser = landsat.Parser(metadata)
        parser.parse()
        sun_azimuth = parser.get_attribute(['L1_METADATA_FILE','IMAGE_ATTRIBUTES','SUN_AZIMUTH'])
        scene_start_time = parser.get_attribute(['searchResponse','metaData','sceneStartTime'])
        self.assertEqual(sun_azimuth, 116.96407755)
        self.assertEqual(scene_start_time, '2013:093:16:49:15.2943749')
    def test_geoye_parser(self):
        '''
        Test an instance of the geowye parser class to check if we can retrieve
        the attributes correctly.
        '''
        import madmex.mapper.parser.geoeye as geoeye
        parser = geoeye.Parser('/LUSTRE/MADMEX/eodata/wv02/11/2012/2012-09-19/lv2a-multi-ortho/12SEP19190058-M2AS-053114634020_01_P001.XML')
        parser.parse()
        ullat = parser.get_attribute(['isd','IMD','BAND_C','ULLAT'])
        self.assertEqual(ullat, 31.06152605)
        
    def test_spot_sensor(self):
        '''
        Test an instance of the spot sensor class to check if it parses its
        attributes correctly.
        '''
        import madmex.mapper.sensor.spot5 as spot
        path = '/LUSTRE/MADMEX/eodata/spot/579312/2009/2009-11-12/1a/579_312_121109_SP5.DIM'
        sensor = spot.Sensor(path)
        self.assertEqual(sensor.get_attribute(spot.ANGLE), float('-8.792839'))
        self.assertEqual(sensor.get_attribute(spot.SENSOR), 'SPOT')
        self.assertEqual(sensor.get_attribute(spot.PLATFORM), '5')
    def test_rapideye_sensor(self):
        '''
        Test an instance of the rapideye sensor class to check if it parses its
        attributes correctly.
        '''
        import madmex.mapper.sensor.rapideye as rapideye
        import datetime
        path = '/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/1447720_2013-02-11_RE3_3A_182802_metadata.xml'
        sensor = rapideye.Sensor(path)
        self.assertEqual(sensor.get_attribute(rapideye.ANGLE), 3.96)
        self.assertEqual(sensor.get_attribute(rapideye.PRODUCT_NAME), 'L3A')
        self.assertEqual(sensor.get_attribute(rapideye.SENSOR), 'OPTICAL')
        self.assertEqual(sensor.get_attribute(rapideye.PLATFORM), 'RE-3')
        self.assertEqual(sensor.get_attribute(rapideye.CREATION_DATE), '2013-04-26T17:48:34Z')
        self.assertEqual(sensor.get_attribute(rapideye.ACQUISITION_DATE), datetime.datetime.strptime('2013-02-11T18:04:21.337522Z', "%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEqual(sensor.get_attribute(rapideye.CLOUDS), 0.0)
        self.assertEqual(sensor.get_attribute(rapideye.AZIMUTH_ANGLE), 278.21)
        self.assertEqual(sensor.get_attribute(rapideye.SOLAR_AZIMUTH), 162.0359)
        self.assertEqual(sensor.get_attribute(rapideye.SOLAR_ZENITH), 56.02738)
        self.assertEqual(sensor.get_attribute(rapideye.TILE_ID), 1447720)
    def test_filesystem_insert_action(self):
        '''
        Creates several dummy files and then persists them into the filesystem.
        '''
        import json
        from madmex.persistence.filesystem.operations import InsertAction
        name = 'coolest_file_ever.txt'
        dictionary = {"one":1, "two":2, "tree":3}
        my_file = open(name, 'w')
        json.dump(dictionary, my_file, indent=4)
        my_file.close()
        action = InsertAction(name, '/LUSTRE/MADMEX/staging/')
        action.act()
        self.assertTrue(action.success, 'Awesome, everything is ok.')
        self.assertTrue(os.path.isfile(action.new_file))
        action.undo()
        self.assertFalse(action.success)
        self.assertFalse(os.path.isfile(action.new_file))
        os.remove(name)
    def test_new_way_of_create_image_from_reference(self):
        from madmex.mapper.data import raster
        from madmex.mapper.data.raster import default_options_for_create_raster_from_reference
        from madmex.mapper.data.raster import create_raster_tiff_from_reference
        from madmex.mapper.data.raster import new_options_for_create_raster_from_reference
        image =  '/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/1447720_2013-02-11_RE3_3A_182802.tif'
        image = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Tarea11/spot/SinNubes/E55582961409182J1A00001/SCENE01'
        gdal_format = "GTiff"
        data_class = raster.Data(image, gdal_format)
        options_to_create = default_options_for_create_raster_from_reference(data_class.metadata)
        output_file = image + '/result_new_create.TIF'
        array = data_class.read_data_file_as_array()
        create_raster_tiff_from_reference(data_class.metadata, options_to_create, output_file, array)
        output_file = image + '/result_new_options.TIF'
        #options_to_create = new_options_for_create_raster_from_reference(data_class.metadata, raster.CREATE_WITH_NUMBER_OF_BANDS, 1, {})
        new_options_for_create_raster_from_reference(data_class.metadata, raster.CREATE_WITH_GEOTRANSFORM_FROM_GCPS, True, options_to_create)
        new_options_for_create_raster_from_reference(data_class.metadata, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], options_to_create)
        create_raster_tiff_from_reference(data_class.metadata, options_to_create, output_file, array)      
    def test_some_sqlalchemy_functions(self):
        from madmex.persistence.database.connection import SESSION_MAKER, RawProduct, Information
        from sqlalchemy import tuple_
        from datetime import datetime
        session = SESSION_MAKER()
        start_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
        end_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
        print session.query(RawProduct.path, Information.resolution).join(RawProduct.information).all()
        print session.query(RawProduct.path, Information.resolution).join(RawProduct.information).all()
        print session.query(RawProduct.ingest_date, Information.resolution).join(RawProduct.information).filter(tuple_(RawProduct.acquisition_date, RawProduct.acquisition_date).op('overlaps')(tuple_(start_date, end_date)) , RawProduct.pk_id == 1).all()
        session.close()

    def test_create_raster_in_memory(self):
        '''
        Create a raster in memory
        '''
        from madmex.mapper.data  import raster
        folder=''
        image = raster.Data(folder, '')
        image.create_raster_in_memory()
    def test_maf_classification(self):
        '''
        Perform classification of maf result
        '''
        import numpy
        from madmex.mapper.data import raster
        from madmex.transformation.mafclassification import calc_threshold_grid
        from madmex.transformation.mafclassification import recode_classes_grid
        from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode
        #image_maf = '/Users/erickpalacios/test_imad_pair_images/result_maf.tif'
        image_maf = '/LUSTRE/MADMEX/staging/antares_test/test_imad_pair_images/result_maf_prueba.tif'
        gdal_format = 'GTiff'
        image_maf_class = raster.Data(image_maf, gdal_format)
        
        pdf_file = get_parent(image_maf) + '/result_maf_pdf.png'

        thresholds = calc_threshold_grid(image_maf_class.read_data_file_as_array(), pdf_file)
        
        result = recode_classes_grid(image_maf_class.read_data_file_as_array(), thresholds)
        
        image_maf_class_output = get_parent(image_maf) + '/result_maf_class.tif'
        
        width, height, bands = image_maf_class.get_attribute(raster.DATA_SHAPE)
        geotransform = image_maf_class.get_attribute(raster.GEOTRANSFORM)
        projection = image_maf_class.get_attribute(raster.PROJECTION)
        
        image_maf_class_result = image_maf_class.create_from_reference(image_maf_class_output, width , height , 1, geotransform, projection, data_type = NumericTypeCodeToGDALTypeCode(numpy.int16))
        
        image_maf_class.write_array(image_maf_class_result, result)    
    def test_maf_image(self):
        '''
        Perform a maf transformation with the result of imad transformation
        '''
        from madmex.mapper.data import raster
        from madmex.transformation import maf
        gdal_format = "GTiff"
        #image_imad = '/Users/erickpalacios/test_imad_pair_images/result_change_detection.tif'
        #image_imad = '/Users/erickpalacios/Documents/CONABIO/Tareas/1_DeteccionCambiosSpot/2_AdapterParaDeteccionDeCambios/Tarea2/res12CambiosMadTransfJulian/593_318_031210_SP5_593_318_021114_SP5_mad.tif'
        image_imad = '/LUSTRE/MADMEX/staging/antares_test/test_imad_pair_images/result_mad_prueba.tif'
        image_imad_class = raster.Data(image_imad, gdal_format)
        width, height , bands = image_imad_class.get_attribute(raster.DATA_SHAPE)
        print 'bands:'
        print bands
        geotransform = image_imad_class.get_attribute(raster.GEOTRANSFORM) 
        projection = image_imad_class.get_attribute(raster.PROJECTION)
        maf_class = maf.Transformation(image_imad_class.read_data_file_as_array())
        maf_class.execute()
        output = get_parent(image_imad) 
        output+= '/result_maf.tif' 
        print output
        image_maf = image_imad_class.create_from_reference(output, width, height, bands-1, geotransform, projection)
        print 'write'
        image_imad_class.write_raster(image_maf, maf_class.output)
    def test_imad_pair_images(self):
        '''
        Perform an imad transformation with two images
        '''
        from madmex.transformation import imad
        from madmex.mapper.data import harmonized
        from madmex.mapper.data import raster
        image1 = '/LUSTRE/MADMEX/eodata/rapideye/1147524/2012/2012-10-18/l3a/2012-10-18T191005_RE3_3A-NAC_11137283_149747.tif'
        image2 = '/LUSTRE/MADMEX/eodata/rapideye/1147524/2013/2013-09-09/l3a/1147524_2013-09-09_RE5_3A_175826.tif'
        #image2 = '/LUSTRE/MADMEX/eodata/spot/556297/2010/2010-01-26/1a/556_297_260110_SP5.img'
        gdal_format = "GTiff"
        image1_data_class =raster.Data(image1, gdal_format)
        image2_data_class = raster.Data(image2, gdal_format)
        harmonized_class = harmonized.Data(image1_data_class, image2_data_class)
        if harmonized_class:
            data_shape_harmonized = harmonized_class.get_attribute(harmonized.DATA_SHAPE)
            width, height, bands = data_shape_harmonized
            geotransform_harmonized = harmonized_class.get_attribute(harmonized.GEOTRANSFORM)
            projection_harmonized = harmonized_class.get_attribute(harmonized.PROJECTION)
            image1_data_array, image2_data_array = harmonized_class.harmonized_arrays(image1_data_class, image2_data_class)
            imad_class = imad.Transformation(image1_data_array, image2_data_array)
            imad_class.execute()
            output = os.path.join(os.path.expanduser('~'),'test_imad_pair_images')
            create_directory_path(output)
            output+= '/result_mad.tif' 
            mad_image = harmonized_class.create_from_reference(output, width, height, (bands+1), geotransform_harmonized, projection_harmonized)
            harmonized_class.write_raster(mad_image, imad_class.output)
            print 'corrlist'
            print imad_class.outcorrlist
    def test_harmonize_pair_images(self):
        '''
        Harmonize pair images based on three criteria: geographical transformation, 
        projection and shape of the data
        '''
        from madmex.mapper.data import harmonized
        from madmex.mapper.data import raster
        image1 = '/LUSTRE/MADMEX/eodata/rapideye/1147524/2012/2012-10-18/l3a/2012-10-18T191005_RE3_3A-NAC_11137283_149747.tif'
        image2 = '/LUSTRE/MADMEX/eodata/rapideye/1147524/2013/2013-09-09/l3a/1147524_2013-09-09_RE5_3A_175826.tif'
        gdal_format = "GTiff"
        image1_data_class = raster.Data(image1, gdal_format)
        image2_data_class = raster.Data(image2, gdal_format)
        harmonized_class = harmonized.Data(image1_data_class, image2_data_class)
        self.assertEqual(harmonized_class.get_attribute(harmonized.XRANGE), 5000)
        self.assertEqual(harmonized_class.get_attribute(harmonized.GEOTRANSFORM), (715500.0, 5.0, 0.0, 2040500.0, 0.0, -5.0))
    def test_get_raster_properties(self):
        '''
        This method tests the extraction of raster properties.
        '''
        from madmex.mapper.data import raster
        folder = '/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/1447720_2013-02-11_RE3_3A_182802.tif'
        gdal_format = 'GTiff'
        data_class = raster.Data(folder, gdal_format)
        data_class.get_attribute(raster.GEOTRANSFORM)
        data_class.get_attribute(raster.FOOTPRINT)
        data_class.get_attribute(raster.DRIVER_METADATA)
        data_class.get_attribute(raster.METADATA_FILE)
    def test_create_image_from_reference(self):
        '''
        Test functionality on creating a raster using numerical data.
        '''
        from madmex.mapper.data import raster
        image =  '/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/1447720_2013-02-11_RE3_3A_182802.tif'
        gdal_format = "GTiff"
        data_class = raster.Data(image, gdal_format)
        geotransform = data_class.get_attribute(raster.GEOTRANSFORM)
        projection = data_class.get_attribute(raster.PROJECTION)
        data_shape = data_class.get_attribute(raster.DATA_SHAPE)
        width = data_shape[0]
        height = data_shape[1]
        number_of_bands = data_shape[2]
        outname = image + 'result.TIF'
        data_array = data_class.read_data_file_as_array()
        data_file = data_class.create_from_reference(outname, width, height, number_of_bands, geotransform, projection)
        data_class.write_raster(data_file, data_array)
            
class UtilTest(unittest.TestCase):
    def test_space_string(self):
        from madmex.util import space_string
        self.assertEqual(space_string(6, '*'), '******')
        self.assertEqual(space_string(4, 'cd'), 'cdcdcdcd')
        self.assertEqual(space_string(-4, 'whatever'), '')
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

    


    