#!/usr/bin/env python3
"""
Script para añadir un endpoint temporal para probar usuarios en la base de datos.
Este endpoint listará los usuarios existentes sin exponer sus contraseñas.

Uso:
    python add_test_users_endpoint.py
"""

import sys
import os
import logging
from importlib import import_module
from sqlalchemy.orm import Session

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Asegurarse de que el directorio actual esté en el path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    # Intenta importar las dependencias necesarias
    from app.api.endpoints import auth
    from app.models.usuario import Usuario
    from app.db.session import get_db
    from fastapi import APIRouter, Depends, HTTPException, status
    
    logger.info("Importaciones exitosas. Comenzando a agregar el endpoint de prueba...")
    
    # Define el endpoint de prueba
    @auth.router.get("/test-users", summary="Lista todos los usuarios para pruebas")
    async def test_users(db: Session = Depends(get_db)):
        """
        Endpoint para visualizar los usuarios existentes en la base de datos.
        **Solo para propósitos de prueba**.
        
        Returns:
            List[Dict]: Lista de usuarios sin información sensible
        """
        try:
            # Obtener todos los usuarios
            users = db.query(Usuario).all()
            
            # Convertir a formato seguro (sin contraseñas)
            result = [
                {
                    "id": user.id,
                    "email": user.email,
                    "nombre": user.nombre,
                    "rol": user.rol.value if hasattr(user.rol, 'value') else str(user.rol),
                    "activo": user.activo,
                    "fecha_registro": user.fecha_registro.isoformat() if user.fecha_registro else None
                }
                for user in users
            ]
            
            return result
        
        except Exception as e:
            logger.error(f"Error al obtener usuarios: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuarios: {str(e)}"
            )
    
    logger.info("✅ Endpoint de prueba '/api/auth/test-users' agregado exitosamente!")
    
except ImportError as e:
    logger.error(f"Error de importación: {str(e)}")
    logger.error("Asegúrate de ejecutar este script desde el directorio raíz del backend")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error inesperado: {str(e)}")
    sys.exit(1) 