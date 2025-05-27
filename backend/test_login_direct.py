#!/usr/bin/env python3
"""
Script de prueba directa del login para diagnosticar problemas de autenticación
"""
import sys
from pathlib import Path

# Añadir el directorio backend al path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.usuario import Usuario
from app.core.security import verify_password, create_access_token
from app.schemas.auth import UserData, Token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_login_process():
    """Simula el proceso completo de login"""
    
    # Datos de prueba
    email = "abogado@legalassista.com"
    password = "Abogado123!"
    
    logger.info(f"🔍 Iniciando prueba de login para: {email}")
    
    db: Session = SessionLocal()
    
    try:
        # 1. Buscar usuario por email
        logger.info("1. Buscando usuario por email...")
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            logger.error(f"❌ Usuario no encontrado: {email}")
            return False
        
        logger.info(f"✅ Usuario encontrado: {usuario.email} (ID: {usuario.id})")
        logger.info(f"   - Nombre: {usuario.nombre}")
        logger.info(f"   - Rol: {usuario.rol.value}")
        logger.info(f"   - Activo: {usuario.activo}")
        
        # 2. Verificar contraseña
        logger.info("2. Verificando contraseña...")
        password_valid = verify_password(password, usuario.password_hash)
        
        if not password_valid:
            logger.error(f"❌ Contraseña incorrecta para usuario: {email}")
            return False
            
        logger.info("✅ Contraseña válida")
        
        # 3. Verificar cuenta activa
        logger.info("3. Verificando cuenta activa...")
        if not usuario.activo:
            logger.error(f"❌ Cuenta no activada: {email}")
            return False
            
        logger.info("✅ Cuenta activa")
        
        # 4. Crear token
        logger.info("4. Creando token de acceso...")
        access_token = create_access_token(
            data={
                "sub": str(usuario.id),
                "email": usuario.email,
                "rol": usuario.rol.value
            }
        )
        
        logger.info("✅ Token creado exitosamente")
        
        # 5. Construir respuesta
        logger.info("5. Construyendo respuesta...")
        user_data = UserData(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            role=usuario.rol.value
        )
        
        token_response = Token(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
        
        logger.info("✅ Respuesta construida exitosamente")
        logger.info(f"   - Token: {access_token[:20]}...")
        logger.info(f"   - Usuario: {user_data.email}")
        logger.info(f"   - Rol: {user_data.role}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante el login: {str(e)}", exc_info=True)
        return False
    finally:
        db.close()

def test_all_users():
    """Prueba el login para todos los usuarios"""
    
    users_to_test = [
        ("abogado@legalassista.com", "Abogado123!"),
        ("admin@legalassista.com", "admin123"),
        ("cliente@legalassista.com", "cliente123")
    ]
    
    logger.info("🧪 Iniciando pruebas de login para todos los usuarios...")
    
    for email, password in users_to_test:
        logger.info(f"\n--- Probando {email} ---")
        success = test_login_with_credentials(email, password)
        if success:
            logger.info(f"✅ Login exitoso para {email}")
        else:
            logger.error(f"❌ Login falló para {email}")

def test_login_with_credentials(email: str, password: str):
    """Prueba login con credenciales específicas"""
    
    db: Session = SessionLocal()
    
    try:
        # Buscar usuario
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            logger.error(f"Usuario no encontrado: {email}")
            return False
        
        # Verificar contraseña
        password_valid = verify_password(password, usuario.password_hash)
        
        if not password_valid:
            logger.error(f"Contraseña incorrecta para: {email}")
            return False
        
        # Verificar cuenta activa
        if not usuario.activo:
            logger.error(f"Cuenta no activa: {email}")
            return False
        
        logger.info(f"Login OK: {email} ({usuario.rol.value})")
        return True
        
    except Exception as e:
        logger.error(f"Error en login {email}: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🚀 Iniciando pruebas de diagnóstico de login...")
    
    # Prueba específica del abogado
    success = test_login_process()
    
    if success:
        logger.info("\n🎉 ¡Login de abogado funciona correctamente!")
    else:
        logger.error("\n💥 ¡Error en el login de abogado!")
    
    # Prueba todos los usuarios
    logger.info("\n" + "="*50)
    test_all_users() 