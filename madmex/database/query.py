'''
Created on Jun 4, 2015

@author: agutierrez
'''

from madmex.database.connection import Person, Base, Address
from sqlalchemy import create_engine

engine = create_engine('sqlite:///sqlalchemy_example.db')

Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker


DBSession = sessionmaker()

DBSession.bind = engine

session = DBSession()

print session.query(Person).all()

person = session.query(Person).first()

print person.name

print session.query(Address).filter(Address.person == person).one()

address = session.query(Address).filter(Address.person == person).one()

print address.post_code

