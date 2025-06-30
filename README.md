
#  API de Reservas de Mesas – FastAPI

Esta es una API desarrollada con FastAPI, SQLAlchemy y SQLite, que permite gestionar mesas y reservas en un restaurante, cumpliendo con las especificaciones de una prueba técnica.

---

##  Instrucciones de instalación y ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/evelyn23293/mesa_reservas.git
cd mesa_reservas
```

### 2. Crear entorno virtual (opcional pero recomendado)
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear la base de datos y datos de prueba
```bash
python init_db.py
```

### 5. Ejecutar el servidor
```bash
uvicorn main:app --reload
```

La API estará disponible en:  
 http://127.0.0.1:8000  
Documentación interactiva:  
 http://127.0.0.1:8000/docs

---

##  Seguridad por API Key

Los endpoints `POST` y `PUT` están protegidos con una API Key.  
Debe enviarse el header:

```http
X-API-Key: supersecreta123
```

Si no se incluye, la API responderá con error 401 Unauthorized.

---

##  Modelo de Datos

### Mesa
- `id`: int
- `nombre`: str
- `capacidad`: int
- `estado`: Enum (`Libre`, `Reservada`, `Ocupada`)

### Reserva
- `id`: int
- `mesa_id`: ForeignKey a Mesa
- `fecha_hora_inicio`: datetime
- `fecha_hora_fin`: datetime
- `num_huespedes`: int
- `nombre_cliente`: str
- `estado`: Enum (`confirmada`, `completada`, `cancelada`)

---

##  Lógica de Disponibilidad

El endpoint `/reservas/disponibilidad` verifica:

- Que la mesa tenga capacidad suficiente
- Que no esté ocupada en el horario solicitado (rango de 2 horas)
- Que no tenga reservas solapadas (ni confirmadas ni activas)
- Que esté marcada como `"Libre"` o `"Reservada"`

---

##  Endpoints disponibles

###  `GET /mesas`
Obtiene todas las mesas.

```bash
curl http://127.0.0.1:8000/mesas
```

---

###  `POST /reservas/disponibilidad`
Consulta mesas libres para una fecha/hora/número de personas.

```bash
curl -X POST http://127.0.0.1:8000/reservas/disponibilidad \
  -H "Content-Type: application/json" \
  -H "X-API-Key: supersecreta123" \
  -d '{
    "fecha": "2025-07-10",
    "hora": "19:00",
    "num_huespedes": 2
}'
```

---

###  `POST /reservas`
Crea una reserva confirmada.

```bash
curl -X POST http://127.0.0.1:8000/reservas \
  -H "Content-Type: application/json" \
  -H "X-API-Key: supersecreta123" \
  -d '{
    "mesa_id": 1,
    "fecha": "2025-07-10",
    "hora": "19:00",
    "num_huespedes": 2,
    "nombre_cliente": "Evelyn"
}'
```

---

###  `GET /reservas/{id}`
Consulta una reserva específica.

```bash
curl http://127.0.0.1:8000/reservas/1
```

---

###  `PUT /reservas/{id}/cancelar`
Cancela una reserva.

```bash
curl -X PUT http://127.0.0.1:8000/reservas/1/cancelar \
  -H "X-API-Key: supersecreta123"
```

---

###  `PUT /reservas/{id}/completar`
Marca la reserva como completada y libera la mesa.

```bash
curl -X PUT http://127.0.0.1:8000/reservas/1/completar \
  -H "X-API-Key: supersecreta123"
```

---

###  `PUT /mesas/{id}/estado`
Cambia el estado de una mesa manualmente.

```bash
curl -X PUT http://127.0.0.1:8000/mesas/1/estado \
  -H "Content-Type: application/json" \
  -H "X-API-Key: supersecreta123" \
  -d '{"estado": "Libre"}'
```

---

##  Transición de estados de mesa

- Al crear una reserva → mesa pasa a `"Reservada"`
- Al completar o cancelar → mesa vuelve a `"Libre"`
- También se puede actualizar manualmente con `PUT /mesas/{id}/estado`

---


##  Autor
Prueba técnica desarrollada por Evelyn Zagarra
Usando FastAPI, SQLAlchemy, SQLite 
