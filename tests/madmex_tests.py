'''
Created on Jun 3, 2015

@author: agutierrez
'''
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


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()