from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime

from app.models.mensaje import Mensaje
from app.models.usuario import Usuario
from app.schemas.chat import MensajeCreate, MensajeResponse

class ChatService:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_connections: Dict[int, List[int]] = {}  # user_id -> [connected_user_ids]

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_connections[user_id] = []

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_message(self, message: str, sender_id: int, receiver_id: int, db: Session):
        # Validar roles
        sender = db.query(Usuario).filter(Usuario.id == sender_id).first()
        receiver = db.query(Usuario).filter(Usuario.id == receiver_id).first()

        if not sender or not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Validar que sea una conversación válida (abogado-cliente)
        if not ((sender.rol == "abogado" and receiver.rol == "cliente") or 
                (sender.rol == "cliente" and receiver.rol == "abogado")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo se permiten conversaciones entre abogados y clientes"
            )

        # Crear y guardar el mensaje
        mensaje = Mensaje(
            remitente_id=sender_id,
            receptor_id=receiver_id,
            contenido=message,
            timestamp=datetime.utcnow()
        )
        db.add(mensaje)
        db.commit()
        db.refresh(mensaje)

        # Enviar mensaje al receptor si está conectado
        if receiver_id in self.active_connections:
            await self.active_connections[receiver_id].send_json({
                "type": "message",
                "data": {
                    "id": mensaje.id,
                    "contenido": mensaje.contenido,
                    "timestamp": mensaje.timestamp.isoformat(),
                    "remitente_id": sender_id,
                    "remitente_nombre": sender.nombre
                }
            })

        return mensaje

    async def mark_as_read(self, message_id: int, user_id: int, db: Session):
        mensaje = db.query(Mensaje).filter(
            Mensaje.id == message_id,
            Mensaje.receptor_id == user_id
        ).first()

        if not mensaje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado"
            )

        mensaje.leido = True
        db.commit()
        return mensaje

    def get_conversation(self, user_id: int, other_user_id: int, db: Session) -> List[Mensaje]:
        return db.query(Mensaje).filter(
            ((Mensaje.remitente_id == user_id) & (Mensaje.receptor_id == other_user_id)) |
            ((Mensaje.remitente_id == other_user_id) & (Mensaje.receptor_id == user_id))
        ).order_by(Mensaje.timestamp).all()

    def get_unread_count(self, user_id: int, db: Session) -> int:
        return db.query(Mensaje).filter(
            Mensaje.receptor_id == user_id,
            Mensaje.leido == False
        ).count()

    def update_user_status(self, user_id: int, online: bool, db: Session):
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user:
            user.online = online
            db.commit() 