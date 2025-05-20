#!/usr/bin/env python3
"""
Script simple para listar los usuarios existentes en la base de datos.

Uso:
    python list_users.py --db-url <url-conexion-db>
"""

import sys
import os
import logging
import argparse
from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Definir las clases y modelos
Base = declarative_base()

class RolUsuario(str, enum.Enum):
    """Roles disponibles en el sistema"""
    ADMIN = "admin"
    ABOGADO = "abogado"
    CLIENTE = "cliente"

class Usuario(Base):
    """Modelo de usuario para la base de datos"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    nombre = Column(String)
    rol = Column(Enum(RolUsuario))
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=func.now())

def parse_args():
    """Parse argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="Lista los usuarios en la base de datos de LegalAssista")
    parser.add_argument(
        "--db-url", 
        type=str, 
        help="URL de conexión a la base de datos"
    )
    return parser.parse_args()

def main():
    """Función principal para listar usuarios en la base de datos"""
    args = parse_args()
    
    # Obtener URL de conexión desde argumentos o variable de entorno
    db_url = args.db_url or os.environ.get('DATABASE_URL')
    
    if not db_url:
        logger.error("Error: No se proporcionó URL de conexión a la base de datos")
        logger.error("Proporciona --db-url o establece la variable de entorno DATABASE_URL")
        sys.exit(1)
    
    # Crear conexión a la base de datos
    logger.info(f"Conectando a la base de datos...")
    
    try:
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Crear sesión
        db = SessionLocal()
        logger.info("Sesión de base de datos iniciada correctamente")
        
        # Mostrar información
        try:
            # Listar todos los usuarios
            all_users = db.query(Usuario).all()
            user_count = len(all_users)
            
            logger.info(f"Total de usuarios en la base de datos: {user_count}")
            logger.info("=== USUARIOS EN LA BASE DE DATOS ===")
            
            for user in all_users:
                rol_str = user.rol.value if hasattr(user.rol, 'value') else str(user.rol)
                fecha_str = user.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if user.fecha_registro else "N/A"
                logger.info(f"ID: {user.id}, Email: {user.email}, Nombre: {user.nombre}, Rol: {rol_str}, Activo: {user.activo}, Fecha: {fecha_str}")
            
            logger.info("=== FIN DEL LISTADO ===")
            
        except Exception as e:
            logger.error(f"Error al listar usuarios: {e}")
        
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()
            logger.info("Sesión de base de datos cerrada correctamente")

if __name__ == "__main__":
    main() 