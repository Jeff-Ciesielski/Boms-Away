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
    unique_parts = relationship('UniquePart', backref='ComponentValue', lazy='dynamic')


class Footprint(Base):
    __tablename__ = 'footprint'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    unique_parts = relationship('UniquePart', backref='Footprint', lazy='dynamic')


class Datasheet(Base):
    __tablename__ = 'datasheet'
    id = Column(Integer, primary_key=True)
    url = Column(String(256), nullable=False)

class UniquePart(Base):
    __tablename__ = 'unique_part'
    id = Column(Integer, primary_key=True)
    component_value_id = Column(Integer, ForeignKey('component_value.id'))
    component_value = relationship('ComponentValue')
    footprint_id = Column(Integer, ForeignKey('footprint.id'))
    footprint = relationship('Footprint')
    manufacturer_pns = relationship('ManufacturerPart', backref='UniquePart', lazy='dynamic')


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
    pn = Column(String(64), nullable=False)
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.id'))
    manufacturer = relationship('Manufacturer')
    unique_part_id = Column(Integer, ForeignKey('unique_part.id'))
    unique_part = relationship('UniquePart')
    supplier_parts = relationship('SupplierPart')

class SupplierPart(Base):
    __tablename__ = 'supplier_part'
    id = Column(Integer, primary_key=True)
    pn = Column(String(64), nullable=False)
    url = Column(String(1024), nullable=True)
    supplier_id = Column(Integer, ForeignKey('supplier.id'))
    supplier = relationship('Supplier')
    manufacturer_part_id = Column(Integer, ForeignKey('manufacturer_part.id'))
    manufacturer_part = relationship('ManufacturerPart')


class Datastore(object):
    def __init__(self, datastore_path):
        self._initialized = False
        self._eng = None

        self._eng = create_engine('sqlite:///{}'.format(datastore_path))
        Base.metadata.create_all(self._eng)
        self._initialized = True

    def _new_session(self):
        if not self._initialized:
            raise Exception("Datastore is not initialized!")

        db_session = sessionmaker()
        db_session.configure(bind=self._eng)

        return db_session()

    def lookup(self, ct):

        session = self._new_session()

        val = (
            session.query(ComponentValue)
            .filter(ComponentValue.value == ct.value)
        ).first()

        fp = (
            session.query(Footprint)
            .filter(Footprint.name == ct.footprint)
        ).first()

        if not val or not fp:
            return None

        up = (
            session.query(UniquePart)
            .filter(UniquePart.component_value == val,
                    UniquePart.footprint == fp)
        ).first()

        return up

    def update(self, ct):

        # TODO: Implement get_or_create, this shit is bananas
        # TODO: Clean up validation
        # Check and update each field

        session = self._new_session()
        
        val = (
            session.query(ComponentValue)
            .filter(ComponentValue.value == ct.value)
        ).first()

        fp = (
            session.query(Footprint)
            .filter(Footprint.name == ct.footprint)
        ).first()

        ds = (
            session.query(Datasheet)
            .filter(Datasheet.url == ct.datasheet)
        ).first()

        mfr = (
            session.query(Manufacturer)
            .filter(Manufacturer.name == ct.manufacturer)
        ).first()

        mpn = (
            session.query(ManufacturerPart)
            .filter(ManufacturerPart.pn == ct.manufacturer_pn)
        ).first()

        spr = (
            session.query(Supplier)
            .filter(Supplier.name == ct.supplier)
        ).first()

        spn = (
            session.query(SupplierPart)
            .filter(SupplierPart.pn == ct.supplier_pn)
        ).first()

        if not val and len(ct.value.strip()):
            val = ComponentValue(value=ct.value)
            session.add(val)

        if not fp and len(ct.footprint.strip()):
            fp = Footprint(name=ct.footprint)
            session.add(fp)

        if not ds and len(ct.datasheet.strip()):
            ds = Datasheet(url=ct.datasheet)
            session.add(ds)

        if not mfr and len(ct.manufacturer.strip()):
            mfr = Manufacturer(name=ct.manufacturer)
            session.add(mfr)

        if not mpn and len(ct.manufacturer_pn.strip()):
            mpn = ManufacturerPart(pn=ct.manufacturer_pn)
            session.add(mpn)

        if not spr and len(ct.supplier.strip()):
            spr = Supplier(name=ct.supplier)
            session.add(spr)

        if not spn and len(ct.supplier_pn.strip()):
            spn = SupplierPart(pn=ct.supplier_pn, url=ct.supplier_url)
            session.add(spn)

        # draw up associations
        if spr and spn and not spn.supplier:
            spn.supplier = spr

        if mfr and mpn and not mpn.manufacturer:
            mpn.manufacturer = mfr

        if mpn and spn:
            spn.manufacturer_part = mpn

        if val and fp:
            # check to see if there is a unique part listing
            up = (
                session.query(UniquePart)
                .filter(UniquePart.component_value == val,
                        UniquePart.footprint == fp)
            ).first()

            if not up:
                up = UniquePart(component_value=val,
                                          footprint=fp)
                session.add(up)

        if mpn:
            mpn.unique_part = up

        session.commit()

    def test_creation():
        eng = create_engine('sqlite://')
        Base.metadata.create_all(eng)

if __name__ == '__main__':
    test_creation()
