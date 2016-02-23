import os

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class ComponentValue(Base):
    __tablename__ = 'component_value'
    id = Column(Integer, primary_key=True)
    value = Column(String(64), nullable=False)
    uniqe_parts = relationship('UniquePart')


class Footprint(Base):
    __tablename__ = 'footprint'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    unique_parts = relationship('UniquePart')


class UniquePart(Base):
    __tablename__ = 'unique_part'
    id = Column(Integer, primary_key=True)
    component_value_id = Column(Integer, ForeignKey('component_value.id'))
    component_value = relationship('ComponentValue')
    footprint_id = Column(Integer, ForeignKey('footprint.id'))
    footprint_value = relationship('Footprint')


class Manufacturer(Base):
    __tablename__ = 'manufacturer'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    website = Column(String(128), nullable=True)
    parts = relationship('ManufacturerPart')


class Supplier(Base):
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    website = Column(String(128), nullable=True)
    parts = relationship('SupplierPart')


class ManufacturerPart(Base):
    __tablename__ = 'manufacturer_part'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.id'))
    manufacturer = relationship('Manufacturer')


class SupplierPart(Base):
    __tablename__ = 'supplier_part'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'))
    supplier = relationship('Supplier')

_initialized = False
_eng = None


def initialize():
    global _initialized
    global _eng
    if _initialized:
        raise Exception("Datastore already initialized!")


    datastore_path = os.path.join(
        os.path.expanduser("~"),
        '.kicadbommgr.d',
        'bommgr.db'
    )

    # TODO: Should we enforce a lockfile here?
    _eng = create_engine('sqlite:///{}'.format(datastore_path))
    Base.metadata.create_all(_eng)
    _initialized = True


def get_session():
    global _initialized
    global _eng
    if not _initialized:
        raise Exception("Datastore is not initialized!")

    db_session = sessionmaker()
    db_session.bind = _eng

    return db_session()


def test_creation():
    eng = create_engine('sqlite://')
    Base.metadata.create_all(eng)


if __name__ == '__main__':
    test_creation()
