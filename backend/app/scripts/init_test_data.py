"""
Script para inicializar datos de prueba en la base de datos.
Crea usuarios, casos, facturas, notificaciones y mensajes para el entorno de prueba.
"""
import logging
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from app.models.caso import Caso
from app.models.factura import Factura
from app.models.notificacion import Notificacion, TipoNotificacion
from app.models.mensaje import Mensaje
from app.core.config import settings
import stripe
from datetime import datetime, timedelta

stripe.api_key = settings.STRIPE_API_KEY

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_test_data(db: Session):
    """Inicializa datos de prueba en la base de datos."""
    try:
        # Verificar si ya existen usuarios de prueba
        admin = db.query(Usuario).filter(Usuario.email == "admin@legalassista.com").first()
        if admin:
            logger.info("Los datos de prueba ya están inicializados")
            return
            
        logger.info("Iniciando creación de datos de prueba...")
        
        # Crear usuarios de prueba
        admin = Usuario(
            email="admin@legalassista.com",
            hashed_password=get_password_hash("Admin123!"),
            nombre="Admin",
            apellido="LegalAssista",
            rol="admin",
            activo=True
        )
        
        abogado = Usuario(
            email="abogado@legalassista.com",
            hashed_password=get_password_hash("Abogado123!"),
            nombre="Juan",
            apellido="Pérez",
            rol="abogado",
            activo=True
        )
        
        cliente = Usuario(
            email="cliente@legalassista.com",
            hashed_password=get_password_hash("Cliente123!"),
            nombre="María",
            apellido="González",
            rol="cliente",
            activo=True
        )
        
        db.add_all([admin, abogado, cliente])
        db.commit()
        logger.info("Usuarios de prueba creados")
        
        # Crear casos de prueba
        caso1 = Caso(
            titulo="Despido injustificado",
            descripcion="Caso de despido sin justificación después de 5 años de trabajo",
            estado="en_proceso",
            cliente_id=cliente.id,
            abogado_id=abogado.id,
            fecha_inicio=datetime.now() - timedelta(days=30)
        )
        
        caso2 = Caso(
            titulo="Incumplimiento de contrato",
            descripcion="Caso de incumplimiento de contrato laboral por parte del empleador",
            estado="nuevo",
            cliente_id=cliente.id,
            fecha_inicio=datetime.now()
        )
        
        db.add_all([caso1, caso2])
        db.commit()
        logger.info("Casos de prueba creados")
        
        # Crear facturas de prueba
        factura1 = Factura(
            caso_id=caso1.id,
            monto=50000,
            estado="pagada",
            fecha_emision=datetime.now() - timedelta(days=15),
            fecha_vencimiento=datetime.now() - timedelta(days=5)
        )
        
        factura2 = Factura(
            caso_id=caso2.id,
            monto=75000,
            estado="pendiente",
            fecha_emision=datetime.now(),
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        
        db.add_all([factura1, factura2])
        db.commit()
        logger.info("Facturas de prueba creadas")
        
        # Crear notificaciones de prueba
        try:
            notificaciones = [
                Notificacion(
                    usuario_id=cliente.id,
                    tipo=TipoNotificacion.NUEVO_CASO,
                    titulo="Nuevo caso creado",
                    mensaje="Se ha creado tu caso de despido injustificado"
                ),
                Notificacion(
                    usuario_id=abogado.id,
                    tipo=TipoNotificacion.ASIGNACION_CASO,
                    titulo="Caso asignado",
                    mensaje="Te han asignado un nuevo caso"
                )
            ]
            
            db.add_all(notificaciones)
            db.commit()
            logger.info("Notificaciones de prueba creadas")
        except Exception as e:
            logger.error(f"Error al crear notificaciones: {str(e)}")
        
        # Crear mensajes de chat de prueba
        try:
            mensajes = [
                Mensaje(
                    caso_id=caso1.id,
                    remitente_id=cliente.id,
                    contenido="Hola, necesito ayuda con mi caso de despido. Trabajé 5 años en la empresa y me despidieron sin justificación.",
                    fecha_envio=datetime.now() - timedelta(days=29)
                ),
                Mensaje(
                    caso_id=caso1.id,
                    remitente_id=abogado.id,
                    contenido="Hola María, entiendo tu situación. Con 5 años de antigüedad tienes derecho a una indemnización. ¿Podrías proporcionarme más detalles sobre tu contrato?",
                    fecha_envio=datetime.now() - timedelta(days=28)
                ),
                Mensaje(
                    caso_id=caso1.id,
                    remitente_id=cliente.id,
                    contenido="Sí, tenía un contrato indefinido. Mi sueldo mensual era de $800.000 y no me pagaron el finiquito.",
                    fecha_envio=datetime.now() - timedelta(days=27)
                ),
                Mensaje(
                    caso_id=caso1.id,
                    remitente_id=abogado.id,
                    contenido="Gracias por la información. En este caso, tendrías derecho a una indemnización aproximada de $4.000.000 más vacaciones proporcionales. Prepararé los documentos para iniciar el proceso.",
                    fecha_envio=datetime.now() - timedelta(days=26)
                )
            ]
            
            db.add_all(mensajes)
            db.commit()
            logger.info("Mensajes de chat de prueba creados")
        except Exception as e:
            logger.error(f"Error al crear mensajes: {str(e)}")
        
        logger.info("Datos de prueba inicializados correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar datos de prueba: {str(e)}")
        db.rollback()

if __name__ == "__main__":
    # Permite ejecutar este script directamente
    from app.db.session import SessionLocal
    db = SessionLocal()
    init_test_data(db)
    db.close() 