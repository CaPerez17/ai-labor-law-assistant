"""
Script para añadir un endpoint temporal para verificar usuarios en la base de datos
"""

from app.api.endpoints import auth
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.usuario import Usuario
import logging

logger = logging.getLogger(__name__)

def add_test_users_endpoint():
    """
    Añade un endpoint temporal para verificar los usuarios en la base de datos.
    Este endpoint debe eliminarse en producción después de realizar las pruebas.
    """
    @auth.router.get("/test-users", summary="Lista todos los usuarios - SOLO PARA DEPURACIÓN")
    async def test_users(db: Session = Depends(get_db)):
        """
        Endpoint temporal para verificar usuarios.
        ATENCIÓN: Este endpoint debe eliminarse en producción 
        después de realizar las pruebas.
        
        Returns:
            list: Lista de usuarios registrados
        """
        try:
            users = db.query(Usuario).all()
            logger.info(f"Consultados {len(users)} usuarios")
            
            # Devolver información limitada para evitar exponer datos sensibles
            return [
                {
                    "id": user.id,
                    "email": user.email,
                    "nombre": user.nombre,
                    "rol": user.rol.value,
                    "activo": user.activo,
                }
                for user in users
            ]
        except Exception as e:
            logger.error(f"Error al consultar usuarios: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )

if __name__ == "__main__":
    # Este script no debe ejecutarse directamente
    # Solo debe importarse desde el módulo principal
    print("Este script no debe ejecutarse directamente.")
    print("Para añadir el endpoint, importa la función add_test_users_endpoint y ejecútala.") 