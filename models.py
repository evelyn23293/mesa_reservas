from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base

class EstadoReserva(str, enum.Enum):
    confirmada = "confirmada"
    completada = "completada"
    cancelada = "cancelada"

class EstadoMesa(str, enum.Enum):
    libre = "Libre"
    ocupada = "Ocupada"
    reservada = "Reservada"

class Mesa(Base):
    __tablename__ = "mesas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True)
    capacidad = Column(Integer)
    estado = Column(Enum(EstadoMesa), default=EstadoMesa.libre)


    reservas = relationship("Reserva", back_populates="mesa")

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    fecha_hora_inicio = Column(DateTime)
    fecha_hora_fin = Column(DateTime)
    num_huespedes = Column(Integer)
    nombre_cliente = Column(String)
    estado = Column(Enum(EstadoReserva), default=EstadoReserva.confirmada)

    mesa = relationship("Mesa", back_populates="reservas")