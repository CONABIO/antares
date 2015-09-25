'''
Created on Sep 25, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

class Colors(object):
    '''
    This class holds string constants to print colors in command line output.
    '''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
