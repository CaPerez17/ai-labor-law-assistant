#!/usr/bin/env python3
"""
Script de startup para el despliegue en producción
Se ejecuta automáticamente al iniciar el servidor
"""
import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_seed_data():
    """Asegurar que los datos de seed están presentes"""
    try:
        # Importar y ejecutar seed
        from app.db.seed import create_test_users, verify_user_credentials
        
        logger.info("🚀 Ejecutando seed de datos de usuario...")
        create_test_users()
        
        logger.info("🔐 Verificando credenciales...")
        if verify_user_credentials():
            logger.info("✅ Seed de datos completado exitosamente")
            return True
        else:
            logger.error("❌ Falló la verificación de credenciales")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en seed de datos: {str(e)}")
        return False

def startup():
    """Función principal de startup"""
    logger.info("🌟 Iniciando proceso de startup...")
    
    # Ejecutar seed de datos
    seed_success = ensure_seed_data()
    
    if seed_success:
        logger.info("✅ Startup completado exitosamente")
    else:
        logger.warning("⚠️ Startup completado con advertencias")
    
    return seed_success

if __name__ == "__main__":
    startup() 