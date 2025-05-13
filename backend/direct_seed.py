#!/usr/bin/env python3
"""
Script directo para inicialización de usuarios en la base de datos
------------------------------------------------------------------
Este script crea usuarios directamente en la base de datos sin depender de los módulos de servicio.
Soporta bases de datos SQLite y PostgreSQL, incluyendo conexión a Render.com.

Uso:
    python direct_seed.py [--postgres "postgresql://user:password@host:port/dbname"]

Si se proporciona --postgres, se usará esa cadena de conexión en lugar de DATABASE_URL.
"""

import os
import sys
import enum
import argparse
from pathlib import Path
from passlib.context import CryptContext

# Configuración de seguridad para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Genera el hash de la contraseña"""
    return pwd_context.hash(password)

def parse_args():
    """Procesa los argumentos de línea de comando"""
    parser = argparse.ArgumentParser(description='Inicializar usuarios en la base de datos.')
    parser.add_argument('--postgres', help='Cadena de conexión PostgreSQL (ej: postgresql://user:pass@host/db)')
    return parser.parse_args()

# Intentar importar las clases necesarias desde sqlalchemy
try:
    from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, func, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    
    args = parse_args()
    
    # Determinar la URL de base de datos a usar
    if args.postgres:
        DATABASE_URL = args.postgres
        print(f"Usando conexión PostgreSQL proporcionada en línea de comando")
    else:
        # Obtener la URL desde las variables de entorno o usar SQLite por defecto
        DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./backend.db")
        print(f"Usando DATABASE_URL: {DATABASE_URL[:20]}...")  # Solo mostrar parte por seguridad
    
    # Crear conexión a la base de datos
    try:
        if DATABASE_URL.startswith("sqlite"):
            engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        else:
            # Para PostgreSQL necesitamos manejar caracteres especiales en contraseñas
            engine = create_engine(DATABASE_URL)
            
        # Verificar la conexión
        with engine.connect() as conn:
            print("✅ Conexión a la base de datos exitosa")
            
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
        
        # Definir clases de modelos para usar directamente
        class RolUsuario(str, enum.Enum):
            """Roles disponibles en el sistema"""
            ADMIN = "admin"
            ABOGADO = "abogado"
            CLIENTE = "cliente"
        
        class Usuario(Base):
            """Modelo de Usuario (versión simplificada)"""
            __tablename__ = "usuarios"
        
            id = Column(Integer, primary_key=True, index=True)
            nombre = Column(String(100), nullable=False)
            email = Column(String(100), unique=True, index=True, nullable=False)
            password_hash = Column(String(255), nullable=False)
            rol = Column(Enum(RolUsuario), nullable=False, default=RolUsuario.CLIENTE)
            fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
            fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
            activo = Column(Boolean, default=True)
        
        # Crear tablas si no existen
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Tablas creadas o ya existentes")
        except Exception as e:
            print(f"⚠️ Error al crear tablas: {e}")
            # No salimos, puede que las tablas ya existan
        
        def create_user(email, password, nombre, rol):
            """Crea un usuario en la base de datos"""
            db = SessionLocal()
            try:
                # Verificar si el usuario ya existe
                existing_user = db.query(Usuario).filter(Usuario.email == email).first()
                
                if existing_user:
                    print(f"El usuario {email} ya existe. Actualizando contraseña...")
                    existing_user.password_hash = get_password_hash(password)
                    existing_user.activo = True
                    db.commit()
                    return existing_user
                
                # Crear nuevo usuario
                user = Usuario(
                    email=email,
                    password_hash=get_password_hash(password),
                    nombre=nombre,
                    rol=rol,
                    activo=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"Usuario creado: {email} (rol: {rol.value})")
                return user
            except Exception as e:
                db.rollback()
                print(f"Error al crear usuario {email}: {e}")
                return None
            finally:
                db.close()
        
        def main():
            """Función principal que crea los usuarios iniciales"""
            print("\n=== INICIANDO SCRIPT DE INICIALIZACIÓN DE USUARIOS ===\n")
            
            # Lista de usuarios a crear
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
                create_user(
                    email=user_data["email"],
                    password=user_data["password"],
                    nombre=user_data["nombre"],
                    rol=user_data["rol"]
                )
            
            print("\nProceso finalizado.")
            
            # Verificar los usuarios creados
            db = SessionLocal()
            try:
                users = db.query(Usuario).all()
                print(f"\nUsuarios en la base de datos ({len(users)}):")
                for user in users:
                    print(f"- {user.email} (rol: {user.rol.value}, activo: {user.activo})")
            finally:
                db.close()
                
            print("\n=== INSTRUCCIONES DE USO ===")
            print("Usuarios disponibles para pruebas:")
            print("1. admin@legalassista.com / admin123 (Administrador)")
            print("2. abogado@legalassista.com / abogado123 (Abogado)")
            print("3. cliente@legalassista.com / cliente123 (Cliente)")
            print("\nUsuarios para modo demo:")
            print("4. admin_demo@legalassista.com / demo123 (Administrador Demo)")
            print("5. abogado_demo@legalassista.com / demo123 (Abogado Demo)")
            print("6. cliente_demo@legalassista.com / demo123 (Cliente Demo)")
        
        if __name__ == "__main__":
            main()
            
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Error al importar dependencias: {e}")
    print("Asegúrate de tener instalado SQLAlchemy y passlib:")
    print("  pip install sqlalchemy passlib")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1) 