#!/usr/bin/env python3
"""
Script directo para inicialización de usuarios en la base de datos
------------------------------------------------------------------
Este script crea usuarios directamente en la base de datos sin depender de los módulos de servicio.
"""

import os
import sys
import enum
from pathlib import Path
from passlib.context import CryptContext

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Genera el hash de la contraseña"""
    return pwd_context.hash(password)

# Intentar importar las clases necesarias desde sqlalchemy
try:
    from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, func, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    
    # Obtener la URL de la base de datos desde las variables de entorno o usar SQLite por defecto
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./backend.db")
    
    # Crear conexión a la base de datos
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)
        
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
    Base.metadata.create_all(bind=engine)
    
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
        print("Iniciando script de inicialización de usuarios...")
        
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
        
        print("Proceso finalizado.")
        
        # Verificar los usuarios creados
        db = SessionLocal()
        try:
            users = db.query(Usuario).all()
            print(f"\nUsuarios en la base de datos ({len(users)}):")
            for user in users:
                print(f"- {user.email} (rol: {user.rol.value}, activo: {user.activo})")
        finally:
            db.close()
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"Error al inicializar el script: {e}")
    sys.exit(1) 