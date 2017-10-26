'''
Created on Oct 3, 2017

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.core.controller.base import BaseCommand
from madmex.util import download_landsat_scene



class Command(BaseCommand):
    '''
    classdocs
    '''


    def handle(self, **options):
        '''
        This command is used to query the catalog database.
        '''
        
        TM = 12266
        ETM = 12267
        OLI = 12864
        
        url = 'https://earthexplorer.usgs.gov/download/%s/%s/STANDARD/EE' % (TM, 'LT50270481995194AAA04')
        
    
        
        download_landsat_scene(url, '/Users/agutierrez/Documents/test', 'LT50270481995194AAA04.tgz')