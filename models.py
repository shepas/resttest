import asyncio
import random

import time
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base, db_session

class Server(Base):
    ''' Модель сервера '''
    __tablename__ = 'Server'
    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime(timezone=True), default=func.now())
    modifyDatetime = Column(DateTime(timezone=True), default=func.now())
    expirationDate = Column(DateTime(timezone=True))
    status_id = Column(Integer, ForeignKey('rbStatus.id'))
    rack_id = Column(Integer, ForeignKey('Rack.id'))

    status = relationship('RbStatus', foreign_keys=[status_id])
    rack = relationship('Rack', foreign_keys=[rack_id])

    def getStatus(self):
        return RbStatus.query.filter(RbStatus.id == self.status_id).first().value if self.status_id else 'Without status'

    def activateServer(self):
        time.sleep(random.randint(10, 20))
        self.status_id = RbStatus.query.filter(RbStatus.value == 'Active').first().id
        db_session.commit()
        return


    def serialize(self):
        return {'id': self.id,
                'createDate': self.createDatetime,
                'modifyDate': self.modifyDatetime,
                'expirationDate': self.expirationDate if self.expirationDate else 'None',
                'status': self.getStatus(),
                'rack': self.rack_id if self.rack_id else 'Not in rack',
                }

class Rack(Base):
    ''' Модель стоек '''
    __tablename__ = 'Rack'
    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime(timezone=True), default=func.now())
    modifyDatetime = Column(DateTime(timezone=True), default=func.now())
    size_id = Column(Integer, ForeignKey('rbSize.id'))

    size = relationship('RbSize', foreign_keys=[size_id])

    def __init__(self, size_id):
        self.size_id = size_id

    def getBuzySlots(self):
        return Server.query.filter(Server.rack_id == self.id).count()

    def getSize(self):
        return RbSize.query.filter(RbSize.id == self.size_id).first().value

    def serialize(self):
        return {'id': self.id,
                'createDate': self.createDatetime,
                'modifyDate': self.modifyDatetime,
                'size': self.getSize(),
                'buzySlots': self.getBuzySlots(),
                }

class RbStatus(Base):
    ''' Модель справочника статусов '''
    __tablename__ = 'rbStatus'
    id = Column(Integer, primary_key=True)
    value = Column(String(64), nullable=False)

    def __init__(self, value=None):
        self.value = value

    def serialize(self):
        return {'id': self.id, 'value': self.value}

class RbSize(Base):
    ''' Модель справочника размеров '''
    __tablename__ = 'rbSize'
    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)

    def __init__(self, value=None):
        self.value = value

    def serialize(self):
        return {'id': self.id, 'value': self.value}