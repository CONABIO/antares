'''
Created on Jun 3, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from __builtin__ import getattr
import os
import unittest

from madmex.core import controller
from madmex.mapper.parser.landsat import Parser

from madmex.configuration import SETTINGS

class Test(unittest.TestCase):

    def test_copyright(self):
        """
        Pulls copyright string and checks format is correct.
        """
        self.assertRegexpMatches(controller.madmex_copyright(), r"MADMex \d{4}-\d{4}")


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass

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

    def test_landsat_parser(self):
        '''
        Test for the landsat parser, creates a parser instance pointing to a
        landsat xml file and then two properties are retrieved.
        '''
        metadata = "/LUSTRE/MADMEX/eodata/etm+/25046/2013/2013-04-03/l1t/LE70250462013093ASN00_MTL.txt"
        parser = Parser(metadata)
        parser.parse()
        sun_azimuth = parser.get_attribute(['L1_METADATA_FILE','IMAGE_ATTRIBUTES','SUN_AZIMUTH'])
        scene_start_time = parser.get_attribute(['searchResponse','metaData','sceneStartTime'])
        self.assertEqual(sun_azimuth, 116.96407755)
        self.assertEqual(scene_start_time, '2013:093:16:49:15.2943749')
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()