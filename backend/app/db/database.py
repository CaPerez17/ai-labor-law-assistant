"""
Configuración de la base de datos
--------------------------------
Este módulo gestiona la conexión a la base de datos PostgreSQL y proporciona
la sesión y el motor de base de datos para la aplicación.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de conexión desde variables de entorno o usar un valor predeterminado
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/laborlaw"
)

# Crear el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear la clase de sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la clase base para los modelos
Base = declarative_base()


# Función para obtener la sesión de la base de datos
def get_db():
    """
    Dependency para obtener una sesión de base de datos.
    Se asegura de cerrar la sesión después de cada solicitud.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 