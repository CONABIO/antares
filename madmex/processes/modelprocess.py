'''
Created on 26/06/2015

@author: erickpalacios
'''
from madmex import load_class

PROCESSES_PACKAGE = 'madmex.processes'

class MadmexProcess(object):
    '''
    classdocs
    '''
    def bundle(self, input_data, flag):
        '''
        Constructor
        '''
        if flag:
            instance_class = self.load_processes_class(PROCESSES_PACKAGE, 'bundle', input_data) #instance class
            instance_class.execute()
            self.bundle_output = instance_class.output
        else:
            self.bundle_output = input_data

    def extract_sensor_metadata(self, input_data, flag):
        if flag:
            instance_class = self.load_processes_class(PROCESSES_PACKAGE, 'extractsensormetadata', self.bundle_output)
            instance_class.execute()
            self.extract_sensor_metadata_output = instance_class.output
        else:
            self.extract_sensor_metadata_output = input_data
    def extract_image_metadata(self, input_data, flag):
        if flag:
            instance_class = self.load_processes_class(PROCESSES_PACKAGE, 'extractimagemetadata', self.bundle_output)
            instance_class.execute()
            self.extract_image_metadata_output = instance_class.output
        else:
            self.extract_image_metadata_output = input_data
        
    
    def applysql(self, input_data):
        '''
        apply sql
        '''
        pass
    def load_processes_class(self, package, name_process, input_data):
        '''
        load_processes_class
        '''
        module = load_class(package, name_process)
        return module.Process(input_data)


