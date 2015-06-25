'''
Created on Jun 3, 2015

@author: agutierrez
'''

from madmex.core.controller.base import BaseCommand
from madmex.processes import Manager


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        add
        '''
        parser.add_argument('--path', nargs='*')

    def handle(self, **options):
        '''
        options
        '''
        path = options['path'][0]
        #a workflow have different kind of processes
        #workflow = ['bundle', 'extractmetadata', 'apply_sql', 'register']
        workflow = ['bundle', 'extractmetadata']
        input_data_workflow = list()
        #for different processes we need different input_data. So input_data is in general a list
        input_data_workflow.append(path)
        for k in range(0, len(workflow)):
            print workflow[k], input_data_workflow[k]
            obj = Manager(workflow[k], input_data_workflow[k])
            obj.execute() #after each process we obtain output_data
            input_data_workflow.append(obj.output_data)
            print input_data_workflow
            