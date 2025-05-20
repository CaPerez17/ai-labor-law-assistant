#!/usr/bin/env python3
"""
Script para crear usuarios directamente en la base de datos de producción
-----------------------------------------------------------------------
Este script crea los usuarios iniciales necesarios para la aplicación,
utilizando una conexión directa a la base de datos.
"""

import sys
import os
import logging
import argparse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Enum, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
from datetime import datetime
from passlib.context import CryptContext

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar el hash de contraseñas (igual que en la aplicación)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Definir Base para los modelos
Base = declarative_base()

# Definir modelos
class RolUsuario(str, enum.Enum):
    """Roles disponibles en el sistema"""
    ADMIN = "admin"
    ABOGADO = "abogado"
    CLIENTE = "cliente"

class Usuario(Base):
    """Modelo de usuario para crear directamente en la base de datos"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=func.now())

def get_password_hash(password: str) -> str:
    """Genera un hash de la contraseña"""
    return pwd_context.hash(password)

def create_user(db, email, password, nombre, rol, activo=True):
    """
    Crea un usuario en la base de datos o actualiza si ya existe
    """
    # Verificar si el usuario ya existe
    existing_user = db.query(Usuario).filter(Usuario.email == email).first()
    
    if existing_user:
        logger.info(f"Usuario {email} ya existe. Actualizando datos...")
        existing_user.nombre = nombre
        existing_user.password_hash = get_password_hash(password)
        existing_user.rol = rol
        existing_user.activo = activo
        db.commit()
        return existing_user
    
    # Crear nuevo usuario
    logger.info(f"Creando nuevo usuario: {email} con rol {rol.value}")
    user = Usuario(
        email=email,
        password_hash=get_password_hash(password),
        nombre=nombre,
        rol=rol,
        activo=activo
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def main():
    """Función principal para crear usuarios"""
    parser = argparse.ArgumentParser(description="Crear usuarios iniciales en la base de datos")
    parser.add_argument("--db-url", required=True, help="URL de conexión a la base de datos")
    args = parser.parse_args()
    
    # Crear motor de base de datos con la URL proporcionada
    engine = create_engine(args.db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info("=== INICIANDO CREACIÓN DE USUARIOS ===")
    logger.info(f"Conectando a la base de datos: {args.db_url.split('@')[-1]}")  # Mostrar solo el host, no la contraseña
    
    # Crear una sesión de base de datos
    db = SessionLocal()
    
    try:
        # Definir usuarios a crear
        users = [
            {
                "email": "admin@legalassista.com",
                "password": "admin123",
                "nombre": "Administrador",
                "rol": RolUsuario.ADMIN
            },
            {
                "email": "abogado@legalassista.com",
                "password": "abogado123",
                "nombre": "Abogado Principal",
                "rol": RolUsuario.ABOGADO
            },
            {
                "email": "cliente@legalassista.com",
                "password": "cliente123",
                "nombre": "Cliente Test",
                "rol": RolUsuario.CLIENTE
            },
            {
                "email": "admin_demo@legalassista.com",
                "password": "demo123",
                "nombre": "Admin Demo",
                "rol": RolUsuario.ADMIN
            },
            {
                "email": "abogado_demo@legalassista.com",
                "password": "demo123",
                "nombre": "Abogado Demo",
                "rol": RolUsuario.ABOGADO
            },
            {
                "email": "cliente_demo@legalassista.com",
                "password": "demo123",
                "nombre": "Cliente Demo",
                "rol": RolUsuario.CLIENTE
            }
        ]
        
        # Crear cada usuario
        for user_data in users:
            user = create_user(
                db=db,
                email=user_data["email"],
                password=user_data["password"],
                nombre=user_data["nombre"],
                rol=user_data["rol"]
            )
            logger.info(f"Usuario procesado: {user.email} (ID: {user.id}, Rol: {user.rol.value})")
        
        # Verificar cuántos usuarios hay en la base de datos
        total_users = db.query(Usuario).count()
        logger.info(f"Total de usuarios en la base de datos: {total_users}")
        
        # Listar todos los usuarios
        logger.info("=== LISTADO DE USUARIOS ===")
        all_users = db.query(Usuario).all()
        for user in all_users:
            logger.info(f"ID: {user.id}, Email: {user.email}, Nombre: {user.nombre}, Rol: {user.rol.value}, Activo: {user.activo}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 