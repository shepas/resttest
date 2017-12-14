from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

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

class Rack(Base):
    ''' Модель стоек '''
    __tablename__ = 'Rack'
    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime(timezone=True), default=func.now())
    modifyDatetime = Column(DateTime(timezone=True), default=func.now())
    size_id = Column(Integer, ForeignKey('rbSize.id'))

    size = relationship('RbSize', foreign_keys=[size_id])

class RbStatus(Base):
    ''' Модель справочника статусов '''
    __tablename__ = 'rbStatus'
    id = Column(Integer, primary_key=True)
    value = Column(String(64), nullable=False)

    def __init__(self, value=None):
        self.value = value

class RbSize(Base):
    ''' Модель справочника размеров '''
    __tablename__ = 'rbSize'
    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)

    def __init__(self, value=None):
        self.value = value