from pydantic import BaseModel
from datetime import datetime

class DisponibilidadRequest(BaseModel):
    fecha: str  # Formato: "2025-07-01"
    hora: str   # Formato: "18:00"
    num_huespedes: int

class MesaResponse(BaseModel):
    id: int
    nombre: str
    capacidad: int
    estado: str

    class Config:
        orm_mode = True  # Para permitir que FastAPI convierta desde SQLAlchemy
class CrearReservaRequest(BaseModel):
    mesa_id: int
    fecha: str  # "2025-07-01"
    hora: str   # "19:00"
    num_huespedes: int
    nombre_cliente: str

class ReservaResponse(BaseModel):
    id: int
    mesa_id: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    num_huespedes: int
    nombre_cliente: str
    estado: str

    class Config:
        orm_mode = True


class ActualizarEstadoMesa(BaseModel):
    estado: str  # "Libre" o "Ocupada"
