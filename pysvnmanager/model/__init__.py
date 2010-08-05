"""The application's model objects"""
from pysvnmanager.model.meta import Session, metadata
from pysvnmanager.model.person import Person


def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
