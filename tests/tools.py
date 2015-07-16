'''
Created on Jul 9, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from datetime import datetime, timedelta
import os
from random import randrange

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseBundle


def create_random_acquisition_date():
    return create_random_date('%Y-%m-%dT%H:%M:%S.%fZ')
def create_random_creation_date():
    return create_random_date('%Y-%m-%dT%H:%M:%SZ')

def create_random_date(time_format):
    d1 = datetime.strptime('1986-03-23', '%Y-%m-%d')
    d2 = datetime.now()
    delta = d2 -d1
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return (d1 + timedelta(seconds=random_second)).strftime(time_format)

def create_random_date_no_format():
    d1 = datetime.strptime('1986-03-23', '%Y-%m-%d')
    d2 = datetime.now()
    delta = d2 -d1
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return d1 + timedelta(seconds=random_second)

class DummyBundle(BaseBundle):
    
    def __init__(self):
        import json
        self.files = []
        names = ['file1.txt', 'file2.txt', 'file3.txt']
        dictionaries = [{'one':1, 'two':2, 'tree':3}, {'four':4, 'five':5, 'six':6, 'seven':7}, {'eight':8, 'nine':9}]
        
        self.target_url = getattr(SETTINGS, 'TEST_FOLDER')
        self.database_object = None
        
        for i in range(len(names)):
            my_file = open(names[i], 'w')
            json.dump(dictionaries[i], my_file, indent=4)
            self.files.append(os.path.abspath(my_file.name))
            my_file.close()
            
        import uuid
        self.uuid_id = str(uuid.uuid4())
        self.acq_date = create_random_date_no_format()
        self.ing_date = create_random_date_no_format()
        self.my_path = self.target_url
        self.my_legend = None
        self.my_geometry = 'my geometry'
        self.my_information = None
        self.my_product_type = None
        self.my_type = 'raw'
            
    def scan(self):
        pass


    def is_consistent(self):
        pass


    def get_files(self):
        return self.files
    
    def get_output_directory(self):
        return self.target_url
    
    def get_database_object(self):
        if not self.database_object:
            import madmex.persistence.database.connection as database
            
            self.database_object = database.RawProduct(
                uuid=self.uuid_id,
                acquisition_date=self.acq_date,
                ingest_date=self.ing_date,
                path=self.my_path,
                legend=self.my_legend,
                geometry=self.my_geometry,
                information=self.my_information,
                product_type=self.my_product_type,
                type=self.my_type
                )
        return self.database_object

class ErrorDummyBundle(DummyBundle):
    
    def __init__(self):
        super(ErrorDummyBundle,self).__init__()
        self.files.append('this_file_does_not_exists.txt')

if __name__ == '__main__':
    error = ErrorDummyBundle()
    print error.get_files()
    
