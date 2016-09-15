#!/usr/bin/env python
# encoding: utf-8
'''
Created on August 15, 2016
@author:     rmartinez

'''

from __future__ import unicode_literals
from madmex.core.controller.base import BaseCommand

import subprocess
import logging
import os
import sys

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the hillshade argument for this command
        '''
        


    def handle(self, **options):
        '''
        
        '''
        
        inputFile  = options['inFile'][0]
        outputFile = options['outFile'][0]
        
        
