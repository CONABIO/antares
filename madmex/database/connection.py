'''
Created on Jun 4, 2015

@author: agutierrez
'''
import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime, Float, Boolean


ANTARES_DATABASE = 'sqlite:///sqlalchemy_example.db'

Base = declarative_base()

class Provider(Base):
    __tablename__ = 'provider'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    description = Column(String)
    
class Satellite(Base):    
    __tablename__ = 'satellite'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    short_name = Column(String, unique = True)
    provider = Column(Integer, ForeignKey('provider.id'))
    
class Raster(Base):
    __tablename__ = 'raster'
    id = Column(Integer, primary_key = True)
    path = Column(String, unique = True)
    hash = Column(String, unique = True)
    acquisition_date = Column(DateTime())
    ingest_date = Column(DateTime())
    geometry = Column(String)
    grid_id = Column(Integer)
    projection = Column(String)
    cloud_percentage = Column(Float)
    elevation_angle = Column(Float)
    rows = Column(Integer)
    columns = Column(Integer)
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



'''
class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship("Employee",
                    backref='company',
                    cascade='all, delete-orphan')

class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    type = Column(String(20))
    company_id = Column(Integer, ForeignKey('company.id'))
    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'employee',
        'with_polymorphic':'*'
    }

class Engineer(Employee):
    __tablename__ = 'engineer'
    id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
    engineer_info = Column(String(50))
    __mapper_args__ = {'polymorphic_identity':'engineer'}

class Manager(Employee):
    __tablename__ = 'manager'
    id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
    manager_data = Column(String(50))
    __mapper_args__ = {'polymorphic_identity':'manager'}

class Raster(Base):
    __tablename__ = 'raster'
    id = Column(Integer, primary_key=True)
    acquisition_date = Column(Date, nullable=True)
    grid_id = Column(Integer, nullable=True)

class Person(Base):
    __tablename__ = 'person'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

class Address(Base):
    __tablename__ = 'address'
    
    id = Column(Integer, primary_key=True)
    street_name = Column(String(250))
    street_number = Column(String(250))
    post_code = Column(String(250), nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship(Person)
'''   
    
engine = create_engine(ANTARES_DATABASE)

Base.metadata.create_all(engine)