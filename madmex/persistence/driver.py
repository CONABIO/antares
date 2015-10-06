'''
Created on Jul 8, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging
import sys
import traceback
from unittest import result
from sqlalchemy import tuple_
from madmex import _
from madmex.persistence.database.connection import SESSION_MAKER, \
    Product, Host, Command, RawProduct, Information
from madmex.persistence.database.connection import SESSION_MAKER, Product, Host, Command, \
    Sensor
import madmex.persistence.database.operations as database
import madmex.persistence.filesystem.operations as filesystem
from madmex.util import create_directory_path


LOGGER = logging.getLogger(__name__)

def persist_bundle(bundle):
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
        if not session.query(Product).filter(Product.path==bundle.get_database_object().path).count():
            for file_name in bundle.get_files():
                actions.append(filesystem.InsertAction(file_name, destination))
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
    images_references_paths = session.query(RawProduct.path).join(RawProduct.information).filter(tuple_(RawProduct.acquisition_date, RawProduct.acquisition_date).op('overlaps')(tuple_(start_date, end_date)) , Information.cloud_percentage <= cloud_cover).all()
    #images_references_paths = session.query(RawProduct.path, Information.sensor).join(RawProduct.information).filter(tuple_(RawProduct.acquisition_date, RawProduct.acquisition_date).op('overlaps')(tuple_(start_date, end_date)) , RawProduct.product_type == product_id, Information.sensor == sensor_id, Information.cloud_percentage <= cloud_cover).all()
    session.close()
    return [tuples[0] for tuples in images_references_paths]
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
