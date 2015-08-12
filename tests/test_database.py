'''
Created on Jul 17, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import os
import unittest

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from madmex.configuration import SETTINGS
from madmex.persistence.database.connection import BASE
from tests.tools import ErrorDummyBundle, DummyBundle


ENGINE = create_engine(getattr(SETTINGS, 'ANTARES_TEST_DATABASE'))

class DatabaseTest(unittest.TestCase):

    def setUp(self):
        BASE.metadata.create_all(bind=ENGINE)  # @UndefinedVariable
        self.database = getattr(SETTINGS, 'ANTARES_TEST_DATABASE')
        self.session = None

    def tearDown(self):
        BASE.metadata.drop_all(bind=ENGINE)  # @UndefinedVariable
        
    def get_session(self):
        if self.session is None:
            klass = sessionmaker(bind=create_engine(self.database))
            self.session = klass()
        return self.session
    
class DatabaseSimpleTests(DatabaseTest):
    def test_database_insert_action(self):
        '''
        Tests a simple insert into the Organization table. This will ensure
        that the connection is properly configured.
        '''
        import madmex.persistence.database.connection as connection 
        from madmex.persistence.database.operations import InsertAction
        organization_name = 'MyOrganization'
        organization = connection.Organization(
            name=organization_name,
            description='An organization to act what I want.',
            country='Robo-Hungarian Empire',
            url='http://placekitten.com/')
        query = 'SELECT count(*) FROM organization WHERE name=\'%s\';' % organization_name
        try:
            action = InsertAction(organization, self.get_session())
            action.act()
            self.get_session().commit()
            result_set = self.get_session().execute(query)
            for row in result_set:
                self.assertGreater(row['count'], 0)
            action.undo()
            self.get_session().commit()
            result_set = self.get_session().execute(query)
            for row in result_set:
                self.assertEqual(row['count'], 0)
        except:
            self.get_session().rollback()
            raise
        finally:
            self.get_session().close()
    
class DatabaseBundleInsertionTest(DatabaseTest):
    def test_persist_bundle_with_error(self):
        '''
        Tests the behavior of persisting a bundle object when the file to
        be persisted in the filesystem does not exists.
        '''
        from madmex.persistence.driver import persist_bundle
        dummy = ErrorDummyBundle()
        persist_bundle(dummy)
        
        query = 'SELECT count(*) FROM product WHERE uuid=\'%s\';' % dummy.uuid_id
        try:
            result_set = self.get_session().execute(query)
            for row in result_set:
                print dir(row.keys)
                print row.keys
                self.assertEqual(row['count'], 0)
            for file_name in dummy.get_files():
                full_path = os.path.join(dummy.get_output_directory(), os.path.basename(file_name))
                self.assertFalse(os.path.isfile(full_path))
        except:
            self.get_session().rollback()
            raise
        finally:
            self.get_session().close()
            
    def persist_bundle(self):
        from madmex.persistence.driver import persist_bundle
        from sqlalchemy import create_engine
        from sqlalchemy.orm.session import sessionmaker
        from madmex.util import remove_file
        dummy = DummyBundle()
        persist_bundle(dummy)
        
        
        my_database = getattr(SETTINGS, 'ANTARES_TEST_DATABASE')
        klass = sessionmaker(bind=create_engine(my_database))
        session = klass()
        query = 'SELECT count(*) FROM product WHERE uuid=\'%s\';' % dummy.uuid_id
        print query
        try:
            result_set = session.execute(query)
            for row in result_set:
                self.assertGreater(row['count'], 0)
            # Delete object from database.
            session.delete(dummy.get_database_object())
            session.commit()
            for file_name in dummy.get_files():
                full_path = os.path.join(dummy.get_output_directory(), os.path.basename(file_name))
                self.assertTrue(os.path.isfile(full_path))
                # Remove file from filesystem.
                remove_file(full_path)
        except:
            session.rollback()
            raise
        finally:
            session.close()
    def persist_bundle_sensor(self):
        from madmex.persistence.driver import persist_bundle
        folder = '/LUSTRE/MADMEX/staging/madmex_antares/test_ingest/556_297_041114_dim_img_spot'
        from sqlalchemy import create_engine
        from sqlalchemy.orm.session import sessionmaker
        from madmex.mapper.bundle.spot import Bundle
        #from madmex.configuration import SETTINGS

        dummy = Bundle(folder)
        #dummy.target = '/LUSTRE/MADMEX/staging/'
        target_url = getattr(SETTINGS, 'TEST_FOLDER')
        print target_url
        #TODO please fix me, horrible hack
        dummy.target = target_url
        persist_bundle(dummy)
        my_database = getattr(SETTINGS, 'ANTARES_TEST_DATABASE')
        klass = sessionmaker(bind=create_engine(my_database))
        session = klass()
        query = 'SELECT count(*) FROM product WHERE uuid=\'%s\';' % dummy.uuid_id

        try:
            result_set = session.execute(query)
            for row in result_set:
                self.assertGreater(row['count'], 0)
            session.delete(dummy.get_database_object())
            session.commit()
            for file_name in dummy.get_files():
                full_path = os.path.join(target_url, os.path.basename(file_name))
                self.assertTrue(os.path.isfile(full_path))
                os.remove(full_path)
        except:
            session.rollback()
            raise
        finally:
            session.close()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()