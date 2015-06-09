from setuptools import setup
from setuptools import find_packages

config = {
    'description': 'Measure Activity Data Mexico',
    'author': 'CONABIO',
    'url': 'http://www.conabio.gob.mx/',
    'download_url': 'http://172.16.15.24:8080/job/Madmex/',
    'author_email': 'agutierrez@conabio.gob.mx',
    'version': '0.1',
    'install_requires': ['nose', 'SQLAlchemy'],
    'packages'=find_packages(),
    'scripts': [],
    'name': 'madmex'
}

setup(**config)