from app.database import engine, SessionLocal
from app.models import Base, Mesa
from sqlalchemy.orm import Session

def init():
    Base.metadata.drop_all(bind=engine)  # Borra todo
    Base.metadata.create_all(bind=engine)  # Crea todo

    session = Session(bind=engine)

    mesas_demo = [
        Mesa(nombre="Mesa 1", capacidad=2),
        Mesa(nombre="Mesa 2", capacidad=4),
        Mesa(nombre="Mesa 3", capacidad=6),
    ]

    session.add_all(mesas_demo)
    session.commit()
    session.close()

if __name__ == "__main__":
    init()