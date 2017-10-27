'''
Created on Oct 27, 2017

@author: agutierrez
'''
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    '''
    classdocs
    '''


    def handle(self, *args, **options):
        print 'hello world'