'''
Created on Jun 3, 2015

@author: agutierrez
'''
import sys

class CommandError(Exception):
    '''
    Exception class indicating a problem while executing a management
    command.
    '''
    pass

class BaseCommand(object):
    '''
    classdocs
    '''

    help = ''
    args = ''
    _called_from_command_line = False
    
    def __init__(self):
        '''
        Constructor
        '''
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def usage(self, subcommand):
        pass
    
    def create_parser(self):
        pass 
           
    def add_argument(self, parser):
        pass
    
    def print_help(self):
        pass
    
    def run_from_argv(self, argv):    
        pass
    
    def execute(self):
        pass
    
    def handle(self):
        pass
