'''
Created on Jun 4, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.sqltypes import DateTime, Float, Boolean

from madmex.configuration import settings


Base = declarative_base()

can_train_table = Table('can_train', Base.metadata,
    Column('product', Integer, ForeignKey('product.id')),
    Column('algorithm', Integer, ForeignKey('algorithm.id'))
)

product_input_table = Table('product_input_table', Base.metadata,
    Column('output_product', Integer, ForeignKey('product.id')),
    Column('input_product', Integer, ForeignKey('product.id'))
)

class Organization(Base):
    __tablename__ = 'organization'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    description = Column(String)
    
class Satellite(Base):    
    __tablename__ = 'satellite'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    short_name = Column(String, unique = True)
    provider = Column(Integer, ForeignKey('organization.id'))
    
class Raster(Base):
    __tablename__ = 'raster'
    id = Column(Integer, primary_key = True)
    path = Column(String, unique = True)
    uuid = Column(String, unique = True)
    acquisition_date = Column(DateTime())
    satellite = Column(Integer, ForeignKey('satellite.id'))
    ingest_date = Column(DateTime())
    geometry = Column(String)
    grid_id = Column(Integer)
    projection = Column(String)
    cloud_percentage = Column(Float)
    elevation_angle = Column(Float)
    rows = Column(Integer)
    columns = Column(Integer)
    bands = Column(Integer)
    resolution = Column(Float)
    type = Column(String(20))
    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'raster'
    }
    
class ProcessedRaster(Raster):
    __mapper_args__ = {
        'polymorphic_identity':'processed'
    }
    processing_date = Column(DateTime())
    
class RawRaster(Raster):
    __mapper_args__ = {
        'polymorphic_identity':'raw'
    }
    
class Shape(Base):
    __tablename__ = 'shape'
    id = Column(Integer, primary_key = True)
    path = Column(String, unique = True)
    uuid = Column(String, unique = True)
    ingest_date = Column(DateTime())
    extent = Column(String)
    type = Column(String(20))
    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'shape'
    }
    
class ProcessedShape(Shape):
    __mapper_args__ = {
        'polymorphic_identity':'processed'
    }
    processing_date = Column(DateTime())
    
class RawShape(Shape):
    __mapper_args__ = {
        'polymorphic_identity':'raw'
    }
    
class Algorithm(Base):
    __tablename__ = 'algorithm'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    description = Column(String)
    command = Column(String(30))
    is_supervised = Column(Boolean)
    
class Legend(Base):
    __tablename__ = 'legend'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    description = Column(String)
    path = Column(String)
    
class Bundle(Base):
    __tablename__ = 'bundle'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    images_regex = Column(String)
    metadata_regex = Column(String)
    filels_regex = Column(String)
    quick_look_regex = Column(String)
    satellite = Column(Integer, ForeignKey('satellite.id'))

class Unit(Base):
    __tablename__ = 'unit'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    unit = Column(String, unique = True)

class Band(Base):
    __tablename__ = 'band'
    id = Column(Integer, primary_key = True)
    satellite = Column(Integer, ForeignKey('satellite.id'), primary_key=True)
    unit = Column(Integer, ForeignKey('unit.id'))
    minimum_wavelength = Column(Float)
    maximum_wavelength = Column(Float)

class Description(Base):
    __tablename__ = ('description')
    id = Column(Integer, primary_key = True)
    description = Column(String, unique = True) 
    creator = Column(Integer, ForeignKey('organization.id'))
    publisher = Column(Integer, ForeignKey('organization.id'))
    
class ProductType(Base):
    __tablename__ = 'product_type'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    short_name = Column(String, unique = True)
    description = Column(Integer, ForeignKey('description.id'))
    
class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key = True)
    algorithm = Column(Integer, ForeignKey('algorithm.id'))
    legend = Column(Integer, ForeignKey('legend.id'))
    raster = Column(Integer, ForeignKey('raster.id'))
    shape = Column(Integer, ForeignKey('shape.id'))    
    product_type = Column(Integer, ForeignKey('product_type.id'))
    can_train = relationship('Algorithm',
                    secondary = can_train_table)  
    product_input_table = relationship('Products',
                    secondary = product_input_table)  
    
class LandCoverProduct(Product):
    date = Column(DateTime())
    
class ChangeDetectionProduct(Product):
    date_from = Column(DateTime())
    date_to = Column(DateTime())

engine = create_engine(getattr(settings, 'ANTARES_DATABASE'))

    

Base.metadata.create_all(engine)