"""
Configuración de la base de datos
--------------------------------
Este módulo gestiona la conexión a la base de datos y proporciona
la sesión y el motor de base de datos para la aplicación.
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Asegurar que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar configuración centralizada
from config import DATABASE_URL

# Crear el motor de la base de datos
# Para SQLite, necesitamos agregar connect_args={"check_same_thread": False}
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

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