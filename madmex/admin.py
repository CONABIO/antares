# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.contrib.gis import admin

from madmex.models import WorldBorder, Segment


admin.site.register(Segment, admin.GeoModelAdmin)