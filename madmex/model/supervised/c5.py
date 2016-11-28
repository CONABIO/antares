'''
Created on Nov 25, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import distutils

import docker

from madmex.configuration import SETTINGS
from madmex.model.base import BaseModel
from madmex.persistence.driver import get_host_from_command
from madmex.remote.dispatcher import RemoteProcessLauncher, LocalProcessLauncher


class Model(BaseModel):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    def fit(self, X, y):
        return BaseModel.fit(self, X, y)


    def predict(self, X):
        return BaseModel.predict(self, X)


    def save(self, filepath):
        return BaseModel.save(self, filepath)


    def load(self, filepath):
        return BaseModel.load(self, filepath)


if __name__ == '__main__':
    print 'hello'
    command = 'run_container'
    import os
    
    print os.pathsep.join(['hello','world'])
    
    command = 'run_container'
    hosts_from_command = get_host_from_command(command)
    remote = RemoteProcessLauncher(hosts_from_command[0])
    arguments = 'docker run --rm ubuntu echo hello remote'
    print remote.execute(arguments)
    
    
    
    print os.environ["PATH"]
    hosts_from_command = get_host_from_command(command)
    local = LocalProcessLauncher()
    executable = distutils.spawn.find_executable('gdalinfo','/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin/:/Applications/Postgres.app/Contents/Versions/9.5/bin/')
    print executable
    arguments = 'docker run --rm ubuntu echo hello local'
    print local.execute(arguments)