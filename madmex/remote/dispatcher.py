'''
Created on Sep 25, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

import abc
import distutils
import logging
import os
import subprocess

from paramiko import SSHClient
from paramiko.client import AutoAddPolicy

from madmex.util.colors import Colors


LOGGER = logging.getLogger(__name__)

class BaseProcessLauncher():
    '''
    Base class for process launcher, implementations can be local or
    remote.
    '''
    __metaclass__ = abc.ABCMeta
    def __init__(self, params):
        '''
        Constructor
        '''

class RemoteProcessLauncher(BaseProcessLauncher):
    '''
    The purpose of this class is to implement an interface to call remote processes
    using ssh. This client is configured through a host specified when the object
    is created. Each instance of this class can connect to one remote machine,
    Once the connection is configured, the remote host can accept and execute
    commands.
    '''
    def __init__(self, host):
        '''
        Constructor that specifies the host to which this object will be connected
        it also declares the ssh_client to be used later.
        '''
        self.host = host
        self.ssh_client = None
        
    def execute(self, shell_string, write_output = False):
        '''
        This method calls the given shell command in the remote host and prints
        out the response from the host.
        '''
        self._get_ssh_client().set_missing_host_key_policy(AutoAddPolicy())
        self._get_ssh_client().load_system_host_keys()
        self._get_ssh_client().connect(
            self.host.hostname,
            username=self.host.user, password=self.host.password
            )
        
        
        LOGGER.info('Command to be executed: %s', shell_string)
        
        stdin, stdout, stderr = self._get_ssh_client().exec_command(shell_string)
        stdin.close()
        LOGGER.info('stdout:')
        if write_output:
            return stdout.read()
        else:
            print Colors.OKGREEN + stdout.read() + Colors.ENDC

        self._get_ssh_client().close()
        
    def _get_ssh_client(self):
        '''
        Convenient lazzy creation of the ssh client, we only create the client
        until we need it.
        '''
        if not self.ssh_client:
            self.ssh_client = SSHClient()
        return self.ssh_client
    
class LocalProcessLauncher(BaseProcessLauncher):
    '''
    This class will implement a launcher for local processes outside
    python. It will solve the problem of looking for the place where
    a executable is located.
    '''
    def __init__(self):
        pass
    
    def execute(self, shell_string, write_output = False):
        '''
        Looks for the executable in the environment and calls it.
        '''
        shell_string_array = shell_string.split(' ')
        shell_string_array[0]  = self._get_executable(shell_string_array [0])
        subprocess.call(shell_string_array)
    
    def _get_executable(self, executable):
        '''
        Looks for the given executable in a list of directories.
        '''
        return distutils.spawn.find_executable(executable, os.pathsep.join([
                                               '/usr/bin',
                                               '/bin',
                                               '/usr/sbin',
                                               '/sbin',
                                               '/usr/local/bin/',
                                               '/Applications/Postgres.app/Contents/Versions/9.5/bin/']))  
