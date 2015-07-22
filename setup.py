from setuptools import setup
from setuptools import find_packages


setup(name='madmex',
  version='1.0',
  description='Measure Activity Data Mexico',
  author='CONABIO',
  author_email='agutierrez@conabio.gob.mx',
  url='http://www.conabio.gob.mx/',
  packages=find_packages(),
  pakcage_data= {'madmex':['locale/es_MX/LC_MESSAGES/*']},
  scripts=['madmex/bin/madmex'],
  zip_safe = False,
 )