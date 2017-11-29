'''
Created on Nov 29, 2017

@author: agutierrez
'''
from django.contrib.gis import admin

from madmex.models import WorldBorder


admin.site.register(WorldBorder, admin.GeoModelAdmin)