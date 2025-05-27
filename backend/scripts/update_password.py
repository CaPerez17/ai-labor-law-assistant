#!/usr/bin/env python3
"""Script para actualizar la contraseña del usuario abogado"""

import os
import sys
from pathlib import Path

# Asegurar que el directorio backend esté en sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base  # Importa todos los modelos
from app.models.usuario import Usuario, RolUsuario
from app.core.security import get_password_hash

# Configuración de la base de datos
DATABASE_URL = "postgresql://legalassista:legalassista@localhost:5432/legalassista"

def update_password():
    """Actualiza la contraseña del usuario abogado"""
    print(f"Conectando a la base de datos: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar usuario abogado
        user = session.query(Usuario).filter(
            Usuario.email == 'abogado@legalassista.com',
            Usuario.rol == RolUsuario.ABOGADO
        ).first()
        
        if not user:
            print("❌ Usuario abogado no encontrado")
            return
        
        # Actualizar contraseña
        new_password = 'Abogado123!'
        user.password_hash = get_password_hash(new_password)
        session.commit()
        
        print("✅ Contraseña actualizada exitosamente")
        print(f"Email: {user.email}")
        print(f"Rol: {user.rol.value}")
        print(f"Nuevo hash: {user.password_hash[:20]}...")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    update_password() 