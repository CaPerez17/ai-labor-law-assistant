#!/usr/bin/env python3
"""
Script simple para crear tablas de base de datos
===============================================
Crea todas las tablas necesarias usando SQLAlchemy ORM
"""

import os
import sys
from pathlib import Path

# Añadir el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

def main():
    print("🔧 Creando tablas de base de datos...")
    
    try:
        # Importar dependencias
        from sqlalchemy import create_engine
        from app.core.config import settings
        from app.db.base import Base
        
        # Crear engine
        print(f"🔗 Conectando a la base de datos...")
        engine = create_engine(settings.DATABASE_URL)
        
        # Crear todas las tablas
        print("🏗️ Creando tablas...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Todas las tablas han sido creadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 