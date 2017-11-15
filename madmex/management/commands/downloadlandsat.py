'''
Created on Oct 3, 2017

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.core.controller.base import BaseCommand
from madmex.management.base import AntaresBaseCommand
from madmex.util import download_landsat_scene


class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--path', nargs=1)
        parser.add_argument('--target', nargs=1)

    def handle(self, **options):
        '''
        This command is used to query the catalog database.
        '''
        path = options['path'][0]
        target = options['target'][0]
        
        TM = 12266
        ETM = 12267
        OLI = 12864
        
        with open(path) as f:
            mylist = f.read().splitlines() 
            for line in mylist:
                url_oli = 'https://earthexplorer.usgs.gov/download/%s/%s/STANDARD/EE' % (OLI, line)
        
                print url_oli
        
                download_landsat_scene(url_oli, target, '%s.tgz' % line)
    

        