'''
Created on Jul 8, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging
from unittest import result
from sqlalchemy import tuple_
from madmex.persistence.database.connection import SESSION_MAKER, \
    Product, Host, Command, RawProduct, Information, Sensor, \
    RapidEyeFootPrintsMexicoOld, Satellite, ProductType
import madmex.persistence.database.operations as database
import madmex.persistence.filesystem.operations as filesystem
from madmex.util import create_directory_path


LOGGER = logging.getLogger(__name__)

def persist_bundle(bundle, keep=False):
    '''
    This function persist a bundle in both the database and the file system. It
    is responsibility of the bundle to provide information about which files
    should be persisted in the file system, and to build the database object
    that will be inserted in the database. The database is configured using the
    session maker in the connection module.
    In order to achieve its purpose, this method creates a list of the actions
    to perform. Once the list is fully populated, it calls the act method for
    each element in the list. If any of the actions in the list fails, a
    rollback is performed in all of them, the result is the same state as before
    the method was called.
    '''
    destination = bundle.get_output_directory()
    create_directory_path(destination)
    actions = []
    session = SESSION_MAKER()
    try:
        if not session.query(Product).filter(Product.product_path == bundle.get_database_object().product_path).count():
            if not keep:
                LOGGER.debug('This process will move the files to a new destination.')
                for file_name in bundle.get_files():
                    actions.append(filesystem.InsertAction(file_name, destination))
            else:
                LOGGER.debug('This process will keep the original path for the files.')
            actions.append(database.InsertAction(
                bundle.get_database_object(),
                session)
                )
            def do_result(action):
                '''
                Lambda function to perform an action and return the result.
                '''
                action.act()
                return action.success
            if not reduce(lambda x, y: x and y, map(do_result, actions)):
                LOGGER.debug('Some action went wrong at persistence process, '
                    'rollback will be performed.')
                for action in actions:
                    action.undo()
            else:
                LOGGER.info('Ingestion was successful.')
        else:
            LOGGER.info('An instance of this object already exist in the database.')
    except Exception:
        LOGGER.error('Not expected error at persistence.driver')
        raise
    finally:
        session.close()
def persist_host(host):
    session = SESSION_MAKER()
    try:
        session.add(host)
        session.commit()
    except Exception:
        LOGGER.error('Not expected error in host insertion.')
        raise
    finally:
        session.close()
def persist_command(command):
    session = SESSION_MAKER()
    try:
        session.add(command)
        session.commit()
    except Exception:
        LOGGER.error('Not expected error in host insertion.')
        raise
    finally:
        session.close()
def query_host_configurations():
    session = SESSION_MAKER()
    try:
        result_set = session.query(Host.pk_id, Host.hostname, Host.configuration).distinct(Host.configuration).all()
    except Exception:
        LOGGER.error('Not expected error in host insertion.')
        raise
    finally:
        session.close()
    return [{'pk_id':result.pk_id, 'hostname':result.hostname, 'configuration':result.configuration} for result in result_set]
def get_host_from_command(command):
    session = SESSION_MAKER()
    try:
        result_set = session.query(Command).join(Host).filter(Command.command == command).all()
        hosts = [result.host for result in result_set]
    except Exception:
        LOGGER.error('Not expected error in host insertion.')
        raise
    finally:
        session.close()
    return hosts 
def find_datasets(start_date, end_date, sensor_id, product_id, cloud_cover, tile_id):
    '''
    Given the parameters of the function find_datasets perform a sqlalchemy orm-query:
    Get the rows in DB that fulfill the condition in the orm-query 
    '''
    session = SESSION_MAKER()
    images_references_paths = session.query(RawProduct.product_path).join(RawProduct.information).filter(tuple_(RawProduct.acquisition_date, RawProduct.acquisition_date).op('overlaps')(tuple_(start_date, end_date)) , Information.cloud_percentage <= cloud_cover, Information.grid_id == tile_id).all()
    # images_references_paths = session.query(RawProduct.path, Information.sensor).join(RawProduct.information).filter(tuple_(RawProduct.acquisition_date, RawProduct.acquisition_date).op('overlaps')(tuple_(start_date, end_date)) , RawProduct.product_type == product_id, Information.sensor == sensor_id, Information.cloud_percentage <= cloud_cover).all()
    session.close()
    return [tuples[0] for tuples in images_references_paths]
def acquisitions_by_mapgrid_and_date(date, mapgrid_target, day_buffer):
    from sqlalchemy import Integer, func, Date
    from sqlalchemy.sql.expression import cast
    session = SESSION_MAKER()
    images_paths = session.query(RawProduct.product_path, RapidEyeFootPrintsMexicoOld.code, RapidEyeFootPrintsMexicoOld.mapgrid2).distinct().join(RawProduct.information).filter(RawProduct.satellite_id == 1, RapidEyeFootPrintsMexicoOld.mapgrid2 == mapgrid_target, cast(RapidEyeFootPrintsMexicoOld.code, Integer) == cast(Information.grid_id, Integer), func.abs(cast(RawProduct.acquisition_date, Date) - date) < day_buffer).all()
    #RawProduct.sensor_id
    return images_paths
def get_sensor_object(sensor_name):
    session = SESSION_MAKER()
    try:
        sensor_object = session.query(Sensor).filter(Sensor.reference_name == sensor_name).first()
    except Exception:
        LOGGER.error('Not expected error in host insertion.')
        raise
    finally:
        session.close()
    return sensor_object 
def get_type_object(type_name):
    session = SESSION_MAKER()
    try:
        print type_name
        type_object = session.query(ProductType).filter(ProductType.short_name == type_name).first()
    except Exception:
        LOGGER.error('Not expected error in host insertion.')
        raise
    finally:
        session.close()
    return type_object 
def get_satellite_object(satellite_name):
    session = SESSION_MAKER()
    try:
        satellite_object = session.query(Satellite).filter(Satellite.name == satellite_name).first()
    except Exception:
        LOGGER.error('Not expected error in host insertion.')
        raise
    finally:
        session.close()
    return satellite_object 
def get_product_type_object(product_type):
    session = SESSION_MAKER()
    try:
        product_type_object = session.query(ProductType).filter(ProductType.short_name == product_type).first()
    except Exception:
        LOGGER.error('Not expected error in host insertion.')
        raise
    finally:
        session.close()
    return product_type_object 
    
if __name__ == '__main__':
    #images_paths = acquisitions_by_mapgrid_and_date('2013-12-31', 15462121, 100)
    #print images_paths
    #print len(images_paths)
    from datetime import datetime
    start_date = datetime.strptime('2015-01-01', "%Y-%m-%d")
    end_date = datetime.strptime( '2015-12-31', "%Y-%m-%d")
    image_paths = find_datasets(start_date, end_date, 12, 1, 10, '21048')
    print image_paths
