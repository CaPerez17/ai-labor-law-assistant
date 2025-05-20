#!/usr/bin/env python3
"""
Script para crear usuarios directamente en la base de datos.

Este script conecta directamente a la base de datos y crea usuarios
con diferentes roles (admin, abogado, cliente y usuarios de demostración).
Incluye manejo de errores y verificación de usuarios existentes.

Uso:
    python create_users_direct.py --db-url <url_conexion_db>
    python create_users_direct.py --admin-only --db-url <url_conexion_db>
    python create_users_direct.py --demo-only --db-url <url_conexion_db>
"""

import sys
import os
import logging
import argparse
from datetime import datetime
from typing import List, Optional, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Importar SQLAlchemy
    from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, func, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    import enum
    from passlib.context import CryptContext
except ImportError as e:
    logger.error(f"Error al importar dependencias: {e}")
    logger.error("Asegúrate de tener instalado sqlalchemy y passlib:")
    logger.error("pip install sqlalchemy passlib")
    sys.exit(1)

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

# Configuración para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Genera un hash de contraseña seguro"""
    return pwd_context.hash(password)

def create_user(db: Session, email: str, password: str, nombre: str, rol: RolUsuario, activo: bool = True) -> Usuario:
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

def parse_args():
    """Parse argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="Crea usuarios en la base de datos de LegalAssista")
    parser.add_argument(
        "--db-url", 
        type=str, 
        help="URL de conexión a la base de datos"
    )
    
    # Grupos de usuarios a crear
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--admin-only", 
        action="store_true", 
        help="Crear solo el usuario administrador"
    )
    group.add_argument(
        "--lawyer-only", 
        action="store_true", 
        help="Crear solo el usuario abogado"
    )
    group.add_argument(
        "--client-only", 
        action="store_true", 
        help="Crear solo el usuario cliente"
    )
    group.add_argument(
        "--demo-only", 
        action="store_true", 
        help="Crear solo los usuarios de demostración"
    )
    
    # Usuario personalizado
    parser.add_argument("--email", type=str, help="Email para usuario personalizado")
    parser.add_argument("--password", type=str, help="Contraseña para usuario personalizado")
    parser.add_argument("--name", type=str, help="Nombre para usuario personalizado")
    parser.add_argument(
        "--role", 
        type=str, 
        choices=["admin", "abogado", "cliente"],
        help="Rol para usuario personalizado"
    )
    
    return parser.parse_args()

def main():
    """Función principal para crear usuarios en la base de datos"""
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
        
        # Crear tablas si no existen
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Tablas creadas o verificadas correctamente")
        except Exception as e:
            logger.warning(f"Advertencia al crear tablas: {e}")
        
        # Crear sesión
        db = SessionLocal()
        logger.info("Sesión de base de datos iniciada correctamente")
        
        # Definir usuarios a crear
        users_to_create = []
        
        # Verificar si es un usuario personalizado
        if args.email and args.password and args.name and args.role:
            rol = RolUsuario(args.role)
            users_to_create.append({
                "email": args.email,
                "password": args.password,
                "nombre": args.name,
                "rol": rol
            })
            logger.info(f"Se creará un usuario personalizado: {args.email} (rol: {args.role})")
        else:
            # Usuarios base del sistema
            if not (args.demo_only or args.lawyer_only or args.client_only):
                # Admin (siempre se crea a menos que se especifique otro grupo exclusivo)
                if not args.lawyer_only and not args.client_only and not args.demo_only:
                    users_to_create.append({
                        "email": "admin@legalassista.com",
                        "password": "admin123",
                        "nombre": "Administrador del Sistema",
                        "rol": RolUsuario.ADMIN
                    })
            
            # Abogado
            if args.lawyer_only or not (args.admin_only or args.client_only or args.demo_only):
                users_to_create.append({
                    "email": "abogado@legalassista.com",
                    "password": "abogado123",
                    "nombre": "Abogado Principal",
                    "rol": RolUsuario.ABOGADO
                })
            
            # Cliente
            if args.client_only or not (args.admin_only or args.lawyer_only or args.demo_only):
                users_to_create.append({
                    "email": "cliente@legalassista.com",
                    "password": "cliente123",
                    "nombre": "Cliente Regular",
                    "rol": RolUsuario.CLIENTE
                })
            
            # Usuarios demo
            if args.demo_only or not (args.admin_only or args.lawyer_only or args.client_only):
                users_to_create.extend([
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
                ])
        
        # Crear usuarios
        created_users = []
        for user in users_to_create:
            try:
                created_user = create_user(
                    db=db,
                    email=user["email"],
                    password=user["password"],
                    nombre=user["nombre"],
                    rol=user["rol"]
                )
                created_users.append(created_user)
            except Exception as e:
                logger.error(f"Error al crear usuario {user['email']}: {e}")
        
        # Mostrar resumen
        user_count = db.query(Usuario).count()
        logger.info(f"Total de usuarios en la base de datos: {user_count}")
        
        # Listar todos los usuarios
        all_users = db.query(Usuario).all()
        logger.info("Usuarios en la base de datos:")
        for user in all_users:
            logger.info(f"ID: {user.id}, Email: {user.email}, Nombre: {user.nombre}, Rol: {user.rol}, Activo: {user.activo}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()
            logger.info("Sesión de base de datos cerrada correctamente")

if __name__ == "__main__":
    main() 