'''
Created on Oct 27, 2017

@author: agutierrez
'''
import csv

from madmex.management.base import AntaresBaseCommand
from madmex.models import LandsatCatalog
from madmex.util import create_file_name, INDEXES, SCENES


FILES = {'ETM':'LANDSAT_ETM_C1.csv',
         'TM':'LANDSAT_TM_C1.csv',
         'LS8':'LANDSAT_8_C1.csv'}

def populate_catalog_django(collection, satellite):
    '''
    This method reads and parses the catalogs from usgs and populates the database
    to fit our needs. Using this approach we don't have to download the scenes in advance,
    instead we download only what we need.
    '''
    index = INDEXES[satellite]        
        
    with open(collection, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            if '%s,%s' % (row[7], row[8]) in SCENES:
                
                scene = LandsatCatalog(
                                scene_id = row[index['scene_id']],
                                landsat_product_id = row[index['landsat_product_id']],
                                sensor = row[index['sensor']],
                                acquisition_date = row[index['acquisition_date']],
                                path = int(row[index['path']]),
                                row = int(row[index['row']]),
                                cloud_full = float(row[index['cloud_full']]),
                                day_night = row[index['day_night']],
                                image_quality = int(row[index['image_quality']]),
                                ground_control_points_model = row[index['ground_control_points_model']],
                                browse_url = row[index['browse_url']])
                scene.save()

class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--directory', nargs=1)

    def handle(self, *args, **options):
        directory = options['directory'][0]
    
        for satellite, filename in FILES.iteritems():
            filepath =  create_file_name(directory, filename)
            populate_catalog_django(filepath, satellite)
            
        print 'Done'
        
        