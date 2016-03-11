'''
Created on Mar 11, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.core.controller.base import BaseCommand
from madmex.mapper.data.harmonized import test

class Command(BaseCommand):
    '''
    classdocs
    '''
    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        test()
