'''
Created on Sep 28, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.persistence.database.connection import Host, Command
from madmex.persistence.driver import persist_host, persist_command


class CommandManager(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    def register_hostname(self, hostname, alias, user, password, port, configuration):
        host = Host(
            hostname=hostname,
            alias=alias,
            user=user,
            password=password,
            port=port,
            configuration=configuration)
        persist_host(host)
        
    def register_command(self, host_id, command, queue):
        command = Command(
            host_id=host_id,
            command=command,
            queue=queue
            )
        persist_command(command)