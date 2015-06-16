'''
Created on Jun 4, 2015

@author: agutierrez
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from madmex.database.connection import Address, Base, Person, Engineer, Company


engine = create_engine('sqlite:///sqlalchemy_example.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)


def i_person(person_name):
    session = DBSession()
    person = Person(name=person_name)
    session.add(person)
    session.commit()
    session.close_all()
    
def i_address(person_name, person_post_code):
    session = DBSession()
    person_object = session.query(Person).filter(Person.name == person_name).one()
    address =  Address(post_code=person_post_code, person = person_object)
    
######################    
    def create_raster(sensor_name):
        satellite = session.query(Satellite).filter(Satellite.name == sensor_name).one()
        raster = Raster(col1,col2,col2, satellite = satellite, )
        return raster
######################    
    
    session.add(address)
    session.commit()
    session.close_all()

def i_company(company_name):
    session = DBSession()
    company = Company(name=company_name)
    session.add(company)
    session.commit()
    session.close_all()
    
    
def i_engineer(person_name, person_company):
    session = DBSession()
    
    companyh = session.query(Company).filter(Company.name == person_company).first()
    engineer= Engineer(engineer_info= 'Description for the new engineer.',
                       company_id = companyh.id)
    session.add(engineer)
    session.commit()
    session.close_all()
    