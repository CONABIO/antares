'''
Created on Jun 4, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from geoalchemy2.types import Geometry
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import Table, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime, Float, Boolean

from madmex.configuration import SETTINGS

BASE = declarative_base()

ENGINE = create_engine(getattr(SETTINGS, 'ANTARES_DATABASE'))

SESSION_MAKER = sessionmaker(ENGINE)

CAN_TRAIN_TABLE = Table(
    'can_train',
    BASE.metadata,
    Column(
        'product',
        Integer,
        ForeignKey('product.pk_id'),
        primary_key=True),
    Column(
        'algorithm',
        Integer,
        ForeignKey('algorithm.pk_id'),
        primary_key=True),
    UniqueConstraint(
        'product', 
        'algorithm', 
        name='can_train_id')
)

# CAN_USE_TABLE = Table(
#     'can_use',
#     BASE.metadata,
#     Column(
#         'group',
#         Integer,
#         ForeignKey('group.pk_id'),
#         primary_key=True),
#     Column(
#         'license',
#         Integer,
#         ForeignKey('license.pk_id'),
#         primary_key=True),
#     UniqueConstraint(
#         'group', 
#         'license', 
#         name='can_use_id')
# )

HAS_SENSOR = Table(
    'has_sensor',
    BASE.metadata,
    Column(
        'satellite',
        Integer,
        ForeignKey('satellite.pk_id'),
        primary_key=True),
    Column(
        'sensor',
        Integer,
        ForeignKey('sensor.pk_id'),
        primary_key=True),
    UniqueConstraint(
        'satellite', 
        'sensor', 
        name='has_sensor_id')
)

# HAS_PRODUCT = Table(
#     'has_product',
#     BASE.metadata,
#     Column(
#         'product',
#         Integer,
#         ForeignKey('product.pk_id'),
#         primary_key=True),
#     Column(
#         'petition',
#         Integer,
#         ForeignKey('petition.pk_id'),
#         primary_key=True),
#     UniqueConstraint(
#         'product', 
#         'petition', 
#         name='has_product_id')
# 
# )

'''
PRODUCT_INPUT_TABLE = Table(
    'product_input_table',
    BASE.metadata,
    Column(
        'input_product',
        Integer,
        ForeignKey('product.pk_id'),
        primary_key=True),
    Column(
        'output_product',
        Integer,
        ForeignKey('product.pk_id'),
        primary_key=True)
)
'''
class Organization(BASE):
    '''
    This table stands for companies or organizations that are somewhat related
    to the system. Imagery providers, satellite developers, government
    organizations all fit in this category.
    '''
    __tablename__ = 'organization'
    pk_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    country = Column(String)
    url = Column(String)
    description = Column(String)
class Sensor(BASE):
    '''
    A sensor is the technology that takes the images. Every sensor can take
    measurements from different wavelengths so they can be used for multiple
    purposes.
    '''
    __tablename__ = 'sensor'
    pk_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
class Satellite(BASE):
    '''
    Satellites are the actual hardware that takes images. A satellite is
    equipped with a sensor, so we have a foreign key pointing to the Sensor
    table. The reason that we have two tables instead of one, is that several
    satellites can have the same sensor installed. The canonical example for
    this is the RapidEye mission that has five satellites equipped with the
    same sensor.
    '''
    __tablename__ = 'satellite'
    pk_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    short_name = Column(String, unique=True)
    launching_date = Column(DateTime())
    terminated = Column(DateTime())
    organization_id = Column(Integer, ForeignKey('organization.pk_id'))
    organization = relationship('Organization')
    has_sensor = relationship(
        'Sensor',
        secondary=HAS_SENSOR)
class Algorithm(BASE):
    '''
    In order to obtain products, raw data must be processed through a series
    of steps, this steps can be classifications, segmentations, cloud
    detection, or atmospheric correction. An algorithm is the process that
    an input had been through to produce some output.
    '''
    __tablename__ = 'algorithm'
    pk_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    command = Column(String(30))
    is_supervised = Column(Boolean)
class Unit(BASE):
    __tablename__ = 'unit'
    pk_id = Column(Integer, primary_key = True)
    name  = Column(String)
    unit = Column(String) 
class Legend(BASE):
    '''
    This table holds the information for the Styled Layer Description. This
    is stored in the form of xml and is used to distribute the products to
    thirdparties. This legends are useful to identify the objects classified
    by the system.
    '''
    __tablename__ = 'legend'
    pk_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    styled_layer_descriptor = Column(String)
    path = Column(String)


# class Temporal(BASE):
#     '''
#     This table stores the temporal location of images to be distributed. This
#     can be deleted over time, but it keeps track of what has been made available
#     through an ftp 
#     '''
#     __tablename__ = 'temporal'
#     pk_id = Column(Integer, primary_key=True)
#     external_url =  Column(String)
#     internal_path = Column(String)
#     init_date = Column(DateTime())
#     end_date = Column(DateTime())
class License(BASE):
    '''
    This table stores the possible license that an image can have.
    '''
    __tablename__ = 'license'
    pk_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    use = Column(String)
    distribution = Column(String)
    product = relationship('Product')
    
# class Group(BASE):
#     '''
#     This table stores information for the groups available for the users. 
#     '''
#     __tablename__ = 'group'
#     pk_id = Column(Integer, primary_key=True)
#     name = Column(String)
#     user = relationship('User')
#     can_use = relationship(
#         'License',
#         secondary=CAN_USE_TABLE)
    
# class User(BASE):
#     '''
#     This table stores information for the users of the system. 
#     '''
#     __tablename__ = 'user'
#     pk_id = Column(Integer, primary_key=True)
#     name = Column(String)
#     last_name_1 = Column(String)
#     last_name_2 = Column(String)
#     role = Column(String)
#     phone = Column(String)
#     email = Column(String)
#     cellphone = Column(String)
#     password = Column(String) 
#     job_position = Column(String)
#     rfc = Column(String)
#     creation_date = Column(DateTime())
#     organization_id = Column(Integer, ForeignKey('organization.pk_id'))
#     organization = relationship('Organization')
#     petition = relationship('Petition')    
#     group_id = Column(Integer, ForeignKey('group.pk_id'))
#     group = relationship('Group')




class Band(BASE):
    '''
    Sensors can measure different intensities of the parts of the light
    spectrum. Each part is then coded into a band in the given image, and each
    band can have a certain resolution.
    '''
    __tablename__ = 'band'
    pk_id = Column(Integer, primary_key=True)
    band_name = Column(String)
    sensor_id = Column(Integer, ForeignKey('sensor.pk_id'))
    bit_depth = Column(Integer)
    band = Column(Integer)
    minimum_wavelength = Column(Float)
    maximum_wavelength = Column(Float)
    sensor = relationship('Sensor')
    name = Column(String, unique=True)
    abrevation = Column(String, unique=True)
    #unit = Column(String)
    unit_id = Column(Integer, ForeignKey('unit.pk_id'))
    unit = relationship("Unit")
class Description(BASE):
    '''
    This table is a link between organizations and products. It provides
    information on who was involved in the development of a product.
    '''
    __tablename__ = ('description')
    pk_id = Column(Integer, primary_key=True)
    description = Column(String, unique=True)
    creator = Column(Integer, ForeignKey('organization.pk_id'))
    publisher_id = Column(Integer, ForeignKey('organization.pk_id'))
    creator = relationship('Organization', backref='creator_id')
    publisher = relationship('Organization', backref='publisher_id')
class Information(BASE):
    '''
    Information stands for metadata, as metadata is a protected word in
    sqlalchemy. This table stores information on each image that can provide
    complex queries of the data without having to access the metadata directly.
    '''
    __tablename__ = 'information'
    pk_id = Column(Integer, primary_key=True)
    metadata_path = Column(String, unique=True)
    grid_id = Column(String)
    projection = Column(String)
    cloud_percentage = Column(Float)
    geometry = Column(Geometry('POLYGON'))
    elevation_angle = Column(Float)
    resolution = Column(Float)
    product = relationship('Product')

class ProductType(BASE):
    '''
    This table has information about the different types of product that the
    system can deliver. This table works as a link between the products, and
    the process that was need to produce it.
    '''
    __tablename__ = 'product_type'
    pk_id = Column(Integer, primary_key=True)
    level = Column(Integer)
    name = Column(String)
    short_name = Column(String, unique=True)
    description_id = Column(Integer, ForeignKey('description.pk_id'))
    description = relationship('Description')
class Product(BASE):
    '''
    A product is either an input or an output of the system. Once an image is
    ingested it becomes a product and can be used to produce new ones. Products
    that come from certain process can be ingested as well and can be used as
    inputs for new processes.
    '''
    __tablename__ = 'product'
    pk_id = Column(Integer, primary_key=True)
    acquisition_date = Column(DateTime())
    ingest_date = Column(DateTime())
    product_path = Column(String, unique=True)
    thumbnail_path = Column(String, unique=True)
    legend = Column(Integer, ForeignKey('legend.pk_id'))
    information_id = Column(Integer, ForeignKey('information.pk_id'))
    information = relationship('Information')
    product_type_id = Column(Integer, ForeignKey('product_type.pk_id'))
    product_type = relationship("ProductType")
    satellite_id = Column(Integer, ForeignKey('satellite.pk_id'))
    satellite = relationship('Satellite')
    algorithm = Column(Integer, ForeignKey('algorithm.pk_id'))
    can_train = relationship(
        'Algorithm',
        secondary=CAN_TRAIN_TABLE)
    license_id = Column(Integer, ForeignKey('license.pk_id'))
    license = relationship('License')
    '''
    input_product = relationship(
        'Product',
        secondary=PRODUCT_INPUT_TABLE,
        primaryjoin=id==PRODUCT_INPUT_TABLE.c.input_product,
        secondaryjoin=id==PRODUCT_INPUT_TABLE.c.output_product,
        backref="output_product")
    '''
    type = Column(String(20))
    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'product'
    }
class RawProduct(Product):
    '''
    A product that has not been processed at all, it can be a raw image just
    ingested to the system.
    '''
    __mapper_args__ = {
        'polymorphic_identity':'raw'
    }
class ProcessedProduct(Product):
    '''
    A product that is the result of a madmex process.
    '''
    __mapper_args__ = {
        'polymorphic_identity':'processed'
    }
    processing_date = Column(DateTime())
# class Petition(BASE):
#     '''
#     This table represents a petition from an external party for a set of images. The
#     images are made available through a service such as ftp.
#     '''
#     __tablename__ = 'petition'
#     pk_id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.pk_id'))
#     user = relationship('User')
#     temporal_id =  Column(Integer, ForeignKey('temporal.pk_id'))
#     temporal = relationship('Temporal')
#     has_product = relationship(
#         'Product',
#         secondary=HAS_PRODUCT)
class Host(BASE):
    '''
    This table has information about the different host in which jobs can be
    remotely executed.
    '''
    __tablename__ = 'host'
    pk_id = Column(Integer, primary_key=True)
    hostname = Column(String, unique=True)
    alias = Column(String)
    user = Column(String)
    password = Column(String)
    port = Column(Integer)
    configuration = Column(String)
class Command(BASE):
    '''
    This table holds information on which command can be executed by each host.
    '''
    __tablename__ = 'command'
    pk_id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('host.pk_id'))
    command = Column(String, unique=True)
    queue = Column(String)
    host = relationship('Host')
    
class RapideyeFeatures(BASE):
    '''
    This table holds features extracted from the rapideye scene.
    '''
    __tablename__ = 'rapideye_features'
    pk_id = Column(Integer, primary_key=True)
    band_1_quant_10 = Column(Float)
    band_2_quant_10 = Column(Float)
    band_3_quant_10 = Column(Float)
    band_4_quant_10 = Column(Float)
    band_5_quant_10 = Column(Float)
    band_1_quant_25 = Column(Float)
    band_2_quant_25 = Column(Float)
    band_3_quant_25 = Column(Float)
    band_4_quant_25 = Column(Float)
    band_5_quant_25 = Column(Float)
    band_1_quant_50 = Column(Float)
    band_2_quant_50 = Column(Float)
    band_3_quant_50 = Column(Float)
    band_4_quant_50 = Column(Float)
    band_5_quant_50 = Column(Float)
    band_1_quant_75 = Column(Float)
    band_2_quant_75 = Column(Float)
    band_3_quant_75 = Column(Float)
    band_4_quant_75 = Column(Float)
    band_5_quant_75 = Column(Float)
    band_1_quant_90 = Column(Float)
    band_2_quant_90 = Column(Float)
    band_3_quant_90 = Column(Float)
    band_4_quant_90 = Column(Float)
    band_5_quant_90 = Column(Float)
    band_1_mean = Column(Float)
    band_2_mean = Column(Float)
    band_3_mean = Column(Float)
    band_4_mean = Column(Float)
    band_5_mean = Column(Float)    
    top = Column(Float)
    left = Column(Float)
    time = Column(Float)
    footprint = Column(Integer)
    path = Column(String, unique=True)


class RapidEyeFootPrintsMexicoOld(BASE):
    # TODO: this is just an example of three columns in the table and two columns mapped
    __table__ = Table('rapideye_footprints_mexico_old', BASE.metadata,
                        Column('gid', Integer, primary_key=True),
                          Column('code', Integer),
                          Column('mapgrid', Integer),
                          Column('mapgrid2', Integer))
    __table_args__ = {'autoload': True, 'autoload_with': ENGINE}
    code = __table__.c.code
    mapgrid = __table__.c.mapgrid
    mapgrid2 = __table__.c.mapgrid2



def create_database():
    '''
    #This method creates the database model in the database engine.
    '''
    #BASE.metadata.create_all(ENGINE)
def delete_database():
    '''
    #This method deletes the database model in the database engine.
    '''
    #BASE.metadata.drop_all(ENGINE)

# a => \u00E1
# e => \u00E9
# i => \u00ED
# o => \u00F3
# u => \u00FA


#def create_vector_tables(path_query):
    #klass = sessionmaker(bind=ENGINE)
    #session = klass()
    #file_open = open(path_query, 'r')
    #sql = " ".join(file_open.readlines())
    #session.execute(sql)
    


if __name__ == '__main__':
    CREATE = 0
    if CREATE:
        # path_query = getattr(SETTINGS, 'RAPIDEYE_FOOTPRINTS_MEXICO_OLD')
        # create_vector_tables(path_query)
        delete_database()
        print 'database deleted'
        print 'vector tables created'
        create_database()
        print 'database created'
        #populate_database()
        print 'database populated'
    else:
        delete_database()
        print 'database deleted'
