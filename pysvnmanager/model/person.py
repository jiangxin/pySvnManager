"""Person model"""
from sqlalchemy import Column
from sqlalchemy.types import Integer, String

from pysvnmanager.model.meta import Base

class Person(Base):
    __tablename__ = "person"

    uid = Column(String(100), primary_key=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    nickname = Column(String(100))
    mail = Column(String(100))

    def __init__(self, uid='', firstname='', lastname='', nickname='', mail=''):
        self.uid = uid
        self.firstname = firstname
        self.lastname = lastname
        self.nickname = nickname
        self.mail = mail

    def __repr__(self):
        return "<Person('%s, %s')" % self.uid

# vim: et ts=4 sw=4
