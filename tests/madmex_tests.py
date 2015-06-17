'''
Created on Jun 3, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from __builtin__ import getattr
import os
import unittest

from madmex.core import controller


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
        
        from madmex.configuration import SETTINGS
        from madmex.configuration import ENVIRONMENT_VARIABLE
        SETTINGS.reload()
        os.environ[ENVIRONMENT_VARIABLE] = path
        print dir(SETTINGS)
        SETTINGS.reload()
        print dir(SETTINGS)
        self.assertEqual(value, getattr(SETTINGS, key.upper()))
        del os.environ[ENVIRONMENT_VARIABLE]
        os.remove(path)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()