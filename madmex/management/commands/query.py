'''
Created on Nov 3, 2017

@author: agutierrez
'''
import os

from madmex.management.base import AntaresBaseCommand
from madmex.models import LansatAWS
from madmex.util import SCENES_MEXICO


class Command(AntaresBaseCommand):
    '''
    classdocs
    '''

    def handle(self, *args, **options):
        
        mexico = '/LUSTRE/MADMEX/tasks/2017_tasks/path_row_mex_col_aus/mexico/path_row_mexico.csv'
        australia = '/LUSTRE/MADMEX/tasks/2017_tasks/path_row_mex_col_aus/australia/path_row_aus.csv'
        colombia = '/LUSTRE/MADMEX/tasks/2017_tasks/path_row_mex_col_aus/colombia/path_row_colombia.csv'
        
        my_files = {'mexico':mexico,'australia':australia, 'colombia':colombia}
        

        for key_file in ['mexico','australia','colombia']:
            csv_file = my_files[key_file]
            with open(csv_file, 'r') as csvfile:
                content = csvfile.read().splitlines()
                for path_row in content:
                    path, row = path_row.split(',')
                    print path, row
                    for year in [2017]:
                        for image in LansatAWS.objects.filter(path=path,row=row,acquisitionDate__year=year):
                            final_path = '/Users/agutierrez/Documents/%s_%s.csv' % (key_file, year)
                            with open(final_path, 'a+') as final_csv_file:
                                format_path = '%03d' % image.path
                                format_row = '%03d' % image.row
                                s3_path = 's3://landsat-pds/c1/L8/%s/%s/%s/' % (format_path, format_row, image.product_id)
                                final_csv_file.write('%s,%s,%s%s' % (image.product_id, image.entity_id, s3_path, os.linesep))
                            final_csv_file.close()

        print 'Done'