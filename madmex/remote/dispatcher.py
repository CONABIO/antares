'''
Created on Sep 25, 2015

@author: agutierrez
'''

from paramiko import SSHClient
from madmex.util.colors import Colors


class RemoteProcessLauncher():
    def __init__(self, host):
        self.host = host
        self.ssh_client = None
        
    def execute(self, shell_string):
        self._get_ssh_client().load_system_host_keys()
        self._get_ssh_client().connect(self.host.hostname, username=self.host.user, password=self.host.password)
        
        
        print "Command to be executed: %s" % shell_string
        
        stdin, stdout, stderr = self._get_ssh_client().exec_command(shell_string)
        stdin.close()
        print "stdout:" 
        print Colors.OKGREEN + stdout.read() + Colors.ENDC
        
    def _get_ssh_client(self):
        if not self.ssh_client:
            self.ssh_client = SSHClient()
        return self.ssh_client
    
