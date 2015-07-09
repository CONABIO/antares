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
from madmex.mapper.base import _get_attribute, BaseBundle
from madmex.mapper.sensor.rapideye import ACQUISITION_DATE
from tests.tools import create_random_acquisition_date, \
    create_random_creation_date, create_random_date_no_format, DummyBundle, \
    ErrorDummyBundle


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
        
    def test_get_attribute(self):
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
        '''
        import madmex.mapper.parser.geoeye as geoeye
        parser = geoeye.Parser('/LUSTRE/MADMEX/eodata/wv02/11/2012/2012-09-19/lv2a-multi-ortho/12SEP19190058-M2AS-053114634020_01_P001.XML')
        parser.parse()
        ullat = parser.get_attribute(['isd','IMD','BAND_C','ULLAT'])
        self.assertEqual(ullat, 31.06152605)
        
    def test_spot_sensor(self):
        import madmex.mapper.sensor.spot as spot
        path = '/LUSTRE/MADMEX/eodata/spot/579312/2009/2009-11-12/1a/579_312_121109_SP5.DIM'
        sensor = spot.Sensor(path)
        self.assertEqual(sensor.get_attribute(spot.ANGLE), float('-8.792839'))
        self.assertEqual(sensor.get_attribute(spot.SENSOR), 'SPOT')
        self.assertEqual(sensor.get_attribute(spot.PLATFORM), '5')
        
    def test_rapideye_sensor(self):
        import madmex.mapper.sensor.rapideye as rapideye
        path = '/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/1447720_2013-02-11_RE3_3A_182802_metadata.xml'
        sensor = rapideye.Sensor(path)
        self.assertEqual(sensor.get_attribute(rapideye.ANGLE), 3.96)
        self.assertEqual(sensor.get_attribute(rapideye.PRODUCT_NAME), 'L3A')
        self.assertEqual(sensor.get_attribute(rapideye.SENSOR), 'OPTICAL')
        self.assertEqual(sensor.get_attribute(rapideye.PLATFORM), 'RE-3')
        self.assertEqual(sensor.get_attribute(rapideye.CREATION_DATE), '2013-04-26T17:48:34Z')
        self.assertEqual(sensor.get_attribute(rapideye.ACQUISITION_DATE), '2013-02-11T18:04:21.337522Z')
        self.assertEqual(sensor.get_attribute(rapideye.CLOUDS), 0.0)
        self.assertEqual(sensor.get_attribute(rapideye.AZIMUTH_ANGLE), 278.21)
        self.assertEqual(sensor.get_attribute(rapideye.SOLAR_AZIMUTH), 162.0359)
        self.assertEqual(sensor.get_attribute(rapideye.SOLAR_ZENITH), 56.02738)
        self.assertEqual(sensor.get_attribute(rapideye.TILE_ID), 1447720)
    def test_database_insert_action(self):
        import madmex.persistence.database.connection as connection 
        from sqlalchemy import create_engine
        from sqlalchemy.orm.session import sessionmaker
        from madmex.persistence.database.operations import InsertAction
        my_database = 'sqlite:///%s' % os.path.abspath('../madmex/persistence/database/sqlite_antares.db');
        klass = sessionmaker(bind=create_engine(my_database))
        session = klass()
        organization_name = 'MyOrganization'
        organization = connection.Organization(
            name=organization_name,
            description='An organization to do what I want.',
            country='Robo-Hungarian Empire',
            url='http://placekitten.com/')
        query = 'SELECT count(*) FROM organization WHERE name="%s";' % organization_name
        try:
            action = InsertAction(organization, session)
            action.do()
            session.commit()
            
            result_set = session.execute(query)
            for row in result_set:
                self.assertGreater(row['count(*)'], 0)
            action.undo()
            session.commit()
            result_set = session.execute(query)
            for row in result_set:
                self.assertEqual(row['count(*)'], 0)
        except:
            session.rollback()
            raise
        finally:
            session.close()
    def test_filesystem_insert_action(self):
        import json
        from madmex.persistence.filesystem.operations import InsertAction
        name = 'coolest_file_ever.txt'
        dictionary = {"one":1, "two":2, "tree":3}
        my_file = open(name, 'w')
        json.dump(dictionary, my_file, indent=4)
        my_file.close()
        action = InsertAction(name, '/LUSTRE/MADMEX/staging/')
        action.do()
        self.assertTrue(action.success, 'Awesome, everything is ok.')
        self.assertTrue(os.path.isfile(action.new_file))
        action.undo()
        self.assertFalse(action.success)
        self.assertFalse(os.path.isfile(action.new_file))
        os.remove(name)
    
        
    def test_persist_bundle_with_error(self):
        from madmex.persistence.driver import persist_bundle
        from sqlalchemy import create_engine
        from sqlalchemy.orm.session import sessionmaker
        dummy = ErrorDummyBundle()
        persist_bundle(dummy)
        
        
        my_database = 'sqlite:///%s' % os.path.abspath('../madmex/persistence/database/sqlite_antares.db');
        klass = sessionmaker(bind=create_engine(my_database))
        session = klass()
        query = 'SELECT count(*) FROM product WHERE uuid="%s";' % dummy.uuid_id
        print query
        try:
            result_set = session.execute(query)
            for row in result_set:
                self.assertEqual(row['count(*)'], 0)
            for file_name in dummy.get_files():
                dest = dummy.get_destination()
                print 'dest: ' + dest
                full_path = os.path.join(dummy.get_destination(), os.path.basename(file_name))
                print full_path
                self.assertFalse(os.path.isfile(full_path))
        except:
            session.rollback()
            raise
        finally:
            session.close()
        
        
        
    def test_persist_bundle(self):
        from madmex.persistence.driver import persist_bundle
        from sqlalchemy import create_engine
        from sqlalchemy.orm.session import sessionmaker
        dummy = DummyBundle()
        persist_bundle(dummy)
        
        
        my_database = 'sqlite:///%s' % os.path.abspath('../madmex/persistence/database/sqlite_antares.db');
        klass = sessionmaker(bind=create_engine(my_database))
        session = klass()
        query = 'SELECT count(*) FROM product WHERE uuid="%s";' % dummy.uuid_id
        print query
        try:
            result_set = session.execute(query)
            for row in result_set:
                self.assertGreater(row['count(*)'], 0)
            # Delete object from database.
            session.delete(dummy.get_database_object())
            session.commit()
            for file_name in dummy.get_files():
                full_path = os.path.join(dummy.get_destination(), os.path.basename(file_name))
                self.assertTrue(os.path.isfile(full_path))
                # Remove file from filesystem.
                os.remove(full_path)
        except:
            session.rollback()
            raise
        finally:
            session.close()
    
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()