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


class Test(unittest.TestCase):

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
    def get_raster_properties(self):
        '''
        Extract some properties of raster
        '''
        from madmex.mapper.data import raster           
            
class UtilTest(unittest.TestCase):
    def test_space_string(self):
        from madmex.util import space_string
        self.assertEqual(space_string(6, '*'), '******')
        self.assertEqual(space_string(4, 'cd'), 'cdcdcdcd')
        self.assertEqual(space_string(-4, 'whatever'), '')
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

    


    