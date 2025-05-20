#!/usr/bin/env python3
"""
Script para crear usuarios en la base de datos de producción
----------------------------------------------------------
Este script crea los usuarios iniciales necesarios para el funcionamiento de la aplicación.
"""

import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asegurar que el directorio backend esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar lo necesario de la aplicación
from app.db.session import SessionLocal
from app.models.usuario import Usuario, RolUsuario
from app.core.security import get_password_hash

def create_user(db, email, password, nombre, rol, activo=True):
    """
    Crea un usuario en la base de datos o actualiza si ya existe
    
    Args:
        db: Sesión de base de datos
        email: Correo electrónico del usuario
        password: Contraseña del usuario
        nombre: Nombre del usuario
        rol: Rol del usuario (debe ser un valor de RolUsuario)
        activo: Si el usuario está activo (por defecto True)
    
    Returns:
        Usuario: El usuario creado o actualizado
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
    logger.info("=== INICIANDO CREACIÓN DE USUARIOS ===")
    
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