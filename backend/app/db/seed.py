#!/usr/bin/env python3
"""
Script de seed para inicializar la base de datos con datos básicos
"""
import sys
from pathlib import Path

# Añadir el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.usuario import Usuario, RolUsuario
from app.models.caso import Caso, EstadoCaso, NivelRiesgo
from app.core.security import get_password_hash
from app.db.base import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_users():
    """Crear usuarios de prueba"""
    db: Session = SessionLocal()
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        # Verificar si ya existe el usuario abogado
        existing_user = db.query(Usuario).filter(Usuario.email == "abogado@legalassista.com").first()
        
        if existing_user:
            logger.info("Usuario abogado ya existe, actualizando contraseña...")
            existing_user.password_hash = get_password_hash("Abogado123!")
            db.commit()
            logger.info("✅ Contraseña del abogado actualizada")
        else:
            logger.info("Creando usuario abogado...")
            
            # Crear usuario abogado
            abogado_user = Usuario(
                email="abogado@legalassista.com",
                nombre="Abogado Test",
                password_hash=get_password_hash("Abogado123!"),
                rol=RolUsuario.ABOGADO,
                activo=True
            )
            
            db.add(abogado_user)
            db.commit()
            logger.info("✅ Usuario abogado creado exitosamente")
        
        # Verificar si existe usuario admin
        existing_admin = db.query(Usuario).filter(Usuario.email == "admin@legalassista.com").first()
        
        if not existing_admin:
            logger.info("Creando usuario admin...")
            
            admin_user = Usuario(
                email="admin@legalassista.com",
                nombre="Admin Test",
                password_hash=get_password_hash("admin123"),
                rol=RolUsuario.ADMIN,
                activo=True
            )
            
            db.add(admin_user)
            db.commit()
            logger.info("✅ Usuario admin creado exitosamente")
        
        # Verificar si existe usuario cliente
        existing_cliente = db.query(Usuario).filter(Usuario.email == "cliente@legalassista.com").first()
        
        if not existing_cliente:
            logger.info("Creando usuario cliente...")
            
            cliente_user = Usuario(
                email="cliente@legalassista.com",
                nombre="Cliente Test",
                password_hash=get_password_hash("cliente123"),
                rol=RolUsuario.CLIENTE,
                activo=True
            )
            
            db.add(cliente_user)
            db.commit()
            logger.info("✅ Usuario cliente creado exitosamente")
        
        # Verificar los usuarios creados
        users = db.query(Usuario).all()
        logger.info(f"Total de usuarios en la base de datos: {len(users)}")
        
        for user in users:
            logger.info(f"- {user.email} ({user.rol.value}) - Activo: {user.activo}")
        
    except Exception as e:
        logger.error(f"Error al crear usuarios: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def create_test_cases():
    """Crear casos de prueba"""
    db: Session = SessionLocal()
    
    try:
        # Obtener usuarios
        abogado = db.query(Usuario).filter(Usuario.email == "abogado@legalassista.com").first()
        cliente = db.query(Usuario).filter(Usuario.email == "cliente@legalassista.com").first()
        
        if not abogado or not cliente:
            logger.warning("No se pueden crear casos: faltan usuarios abogado o cliente")
            return
        
        # Verificar si ya existen casos
        existing_cases = db.query(Caso).count()
        
        if existing_cases > 0:
            logger.info(f"Ya existen {existing_cases} casos en la base de datos")
            return
        
        # Crear casos dummy
        casos_dummy = [
            {
                "titulo": "Caso Dummy - Despido Injustificado",
                "descripcion": "Caso de prueba para verificar comunicación cliente-abogado. El cliente reporta despido sin justa causa.",
                "estado": EstadoCaso.PENDIENTE_VERIFICACION,
                "nivel_riesgo": NivelRiesgo.MEDIO,
                "cliente_id": cliente.id,
                "abogado_id": abogado.id,
                "comentarios": "Caso dummy para testing de la funcionalidad abogado"
            },
            {
                "titulo": "Consulta sobre Horas Extras",
                "descripcion": "Cliente consulta sobre pago de horas extras no reconocidas por la empresa.",
                "estado": EstadoCaso.PENDIENTE,
                "nivel_riesgo": NivelRiesgo.BAJO,
                "cliente_id": cliente.id,
                "abogado_id": abogado.id,
                "comentarios": None
            },
            {
                "titulo": "Acoso Laboral",
                "descripcion": "Reporte de acoso laboral por parte del supervisor directo.",
                "estado": EstadoCaso.EN_PROCESO,
                "nivel_riesgo": NivelRiesgo.ALTO,
                "cliente_id": cliente.id,
                "abogado_id": abogado.id,
                "comentarios": "Caso requiere atención urgente"
            }
        ]
        
        for caso_data in casos_dummy:
            caso = Caso(**caso_data)
            db.add(caso)
        
        db.commit()
        logger.info(f"✅ Creados {len(casos_dummy)} casos dummy exitosamente")
        
        # Mostrar casos creados
        casos = db.query(Caso).all()
        for caso in casos:
            logger.info(f"- Caso {caso.id}: {caso.titulo} ({caso.estado.value})")
        
    except Exception as e:
        logger.error(f"Error al crear casos dummy: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_user_credentials():
    """Verificar que las credenciales del abogado funcionen"""
    from app.core.security import verify_password
    
    db: Session = SessionLocal()
    
    try:
        user = db.query(Usuario).filter(Usuario.email == "abogado@legalassista.com").first()
        
        if user:
            # Verificar contraseña
            is_valid = verify_password("Abogado123!", user.password_hash)
            logger.info(f"Verificación de contraseña para abogado: {'✅ VÁLIDA' if is_valid else '❌ INVÁLIDA'}")
            
            # Mostrar información del usuario
            logger.info(f"Email: {user.email}")
            logger.info(f"Nombre: {user.nombre}")
            logger.info(f"Rol: {user.rol.value}")
            logger.info(f"Activo: {user.activo}")
            logger.info(f"Hash: {user.password_hash[:20]}...")
            
            return is_valid
        else:
            logger.error("❌ Usuario abogado no encontrado")
            return False
            
    except Exception as e:
        logger.error(f"Error al verificar credenciales: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🚀 Iniciando seed de la base de datos...")
    
    # Crear usuarios
    create_test_users()
    
    # Crear casos dummy
    create_test_cases()
    
    # Verificar credenciales
    logger.info("🔐 Verificando credenciales...")
    if verify_user_credentials():
        logger.info("✅ Seed completado exitosamente")
    else:
        logger.error("❌ Error en la verificación de credenciales")
        sys.exit(1) 