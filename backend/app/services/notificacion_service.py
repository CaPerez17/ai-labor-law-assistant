from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from typing import List, Optional, Dict, Any

from app.models.notificacion import Notificacion, TipoNotificacion
from app.models.usuario import Usuario
from app.services.email_service import EmailService
from app.core.config import settings

class NotificacionService:
    def __init__(self):
        self.email_service = EmailService()

    async def crear_notificacion(
        self,
        db: Session,
        usuario_id: int,
        tipo: TipoNotificacion,
        titulo: str,
        mensaje: str,
        datos_adicionales: Optional[Dict[str, Any]] = None,
        enviar_email: bool = True
    ) -> Notificacion:
        """Crea una nueva notificación y opcionalmente envía un email"""
        # Crear notificación en base de datos
        notificacion = Notificacion(
            usuario_id=usuario_id,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            datos_adicionales=json.dumps(datos_adicionales) if datos_adicionales else None
        )
        db.add(notificacion)
        db.commit()
        db.refresh(notificacion)

        # Enviar email si está habilitado
        if enviar_email:
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            if usuario and usuario.recibir_emails:
                await self.email_service.enviar_notificacion(
                    email=usuario.email,
                    nombre=usuario.nombre,
                    titulo=titulo,
                    mensaje=mensaje
                )

        return notificacion

    async def obtener_notificaciones(
        self,
        db: Session,
        usuario_id: int,
        solo_no_leidas: bool = False,
        limite: int = 50
    ) -> List[Notificacion]:
        """Obtiene las notificaciones de un usuario"""
        query = db.query(Notificacion).filter(
            Notificacion.usuario_id == usuario_id,
            Notificacion.fecha_creacion >= datetime.utcnow() - timedelta(days=30)
        )

        if solo_no_leidas:
            query = query.filter(Notificacion.leido == False)

        return query.order_by(Notificacion.fecha_creacion.desc()).limit(limite).all()

    async def marcar_como_leida(
        self,
        db: Session,
        notificacion_id: int,
        usuario_id: int
    ) -> Notificacion:
        """Marca una notificación como leída"""
        notificacion = db.query(Notificacion).filter(
            Notificacion.id == notificacion_id,
            Notificacion.usuario_id == usuario_id
        ).first()

        if notificacion:
            notificacion.leido = True
            notificacion.fecha_lectura = datetime.utcnow()
            db.commit()
            db.refresh(notificacion)

        return notificacion

    async def marcar_todas_como_leidas(
        self,
        db: Session,
        usuario_id: int
    ) -> int:
        """Marca todas las notificaciones de un usuario como leídas"""
        result = db.query(Notificacion).filter(
            Notificacion.usuario_id == usuario_id,
            Notificacion.leido == False
        ).update({
            "leido": True,
            "fecha_lectura": datetime.utcnow()
        })
        db.commit()
        return result

    async def contar_no_leidas(
        self,
        db: Session,
        usuario_id: int
    ) -> int:
        """Cuenta las notificaciones no leídas de un usuario"""
        return db.query(Notificacion).filter(
            Notificacion.usuario_id == usuario_id,
            Notificacion.leido == False,
            Notificacion.fecha_creacion >= datetime.utcnow() - timedelta(days=30)
        ).count()

    async def eliminar_antiguas(
        self,
        db: Session,
        dias: int = 30
    ) -> int:
        """Elimina notificaciones más antiguas que el número de días especificado"""
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        result = db.query(Notificacion).filter(
            Notificacion.fecha_creacion < fecha_limite
        ).delete()
        db.commit()
        return result 