from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import Mesa, Reserva
from app.schemas import (
    DisponibilidadRequest,
    MesaResponse,
    CrearReservaRequest,
    ReservaResponse,
    ActualizarEstadoMesa
)

from fastapi import Header

def verificar_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida")

app = FastAPI()

# CORS (útil si luego conectas con n8n o un frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para usar la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/mesas")
def listar_mesas(db: Session = Depends(get_db)):
    return db.query(Mesa).all()

@app.post("/reservas/disponibilidad", response_model=list[MesaResponse], dependencies=[Depends(verificar_api_key)])
def disponibilidad_mesas(request: DisponibilidadRequest, db: Session = Depends(get_db)):
    # Convertir fecha y hora en datetime
    try:
        fecha_hora_inicio = datetime.strptime(f"{request.fecha} {request.hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha u hora inválido")

    duracion = timedelta(hours=2)
    fecha_hora_fin = fecha_hora_inicio + duracion

    # 1. Filtrar mesas por capacidad
    mesas = db.query(Mesa).filter(Mesa.capacidad >= request.num_huespedes).all()

    disponibles = []
    for mesa in mesas:
        # Verificar si tiene reservas que se solapan
        reservas = db.query(Reserva).filter(
            Reserva.mesa_id == mesa.id,
            Reserva.estado == "confirmada",
            Reserva.fecha_hora_inicio < fecha_hora_fin,
            Reserva.fecha_hora_fin > fecha_hora_inicio
        ).all()

        if not reservas:
            disponibles.append(mesa)

    return disponibles

@app.post("/reservas", response_model=ReservaResponse, dependencies=[Depends(verificar_api_key)])
def crear_reserva(request: CrearReservaRequest, db: Session = Depends(get_db)):
    try:
        fecha_hora_inicio = datetime.strptime(f"{request.fecha} {request.hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha u hora inválido")

    duracion = timedelta(hours=2)
    fecha_hora_fin = fecha_hora_inicio + duracion

    # Validar que la mesa existe
    mesa = db.query(Mesa).filter(Mesa.id == request.mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")

    # Verificar si la mesa ya tiene una reserva solapada
    reservas_solapadas = db.query(Reserva).filter(
        Reserva.mesa_id == request.mesa_id,
        Reserva.estado == "confirmada",
        Reserva.fecha_hora_inicio < fecha_hora_fin,
        Reserva.fecha_hora_fin > fecha_hora_inicio
    ).all()

    if reservas_solapadas:
        raise HTTPException(status_code=400, detail="La mesa ya está reservada en ese horario")

    # Crear la reserva
    nueva_reserva = Reserva(
        mesa_id=request.mesa_id,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        num_huespedes=request.num_huespedes,
        nombre_cliente=request.nombre_cliente,
        estado="confirmada"
    )

    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    mesa.estado = "Reservada"
    db.commit()

    return nueva_reserva

@app.get("/reservas/{reserva_id}", response_model=ReservaResponse)
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


@app.put("/reservas/{reserva_id}/cancelar", response_model=ReservaResponse, dependencies=[Depends(verificar_api_key)])
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    reserva.estado = "cancelada"
    mesa = db.query(Mesa).filter(Mesa.id == reserva.mesa_id).first()
    mesa.estado = "Libre"
    db.commit()
    db.refresh(reserva)
    return reserva

@app.put("/mesas/{mesa_id}/estado", dependencies=[Depends(verificar_api_key)])
def actualizar_estado_mesa(mesa_id: int, request: ActualizarEstadoMesa, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")

    if request.estado not in ["Libre", "Ocupada"]:
        raise HTTPException(status_code=400, detail="Estado inválido. Debe ser 'Libre' u 'Ocupada'.")

    mesa.estado = request.estado
    db.commit()
    db.refresh(mesa)
    return {"mensaje": f"Estado actualizado a {mesa.estado}"}


@app.put("/reservas/{reserva_id}/completar", response_model=ReservaResponse, dependencies=[Depends(verificar_api_key)])
def completar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    reserva.estado = "completada"

    mesa = db.query(Mesa).filter(Mesa.id == reserva.mesa_id).first()
    mesa.estado = "Libre"

    db.commit()
    db.refresh(reserva)
    return reserva

API_KEY = "supersecreta123"
