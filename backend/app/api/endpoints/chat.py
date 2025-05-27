from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.chat import MensajeCreate, MensajeResponse, ConversacionResponse
from app.services.chat_service import ChatService
from app.core.websocket import ConnectionManager

router = APIRouter()
chat_service = ChatService()
manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    try:
        await chat_service.connect(websocket, user_id)
        chat_service.update_user_status(user_id, True, db)
        
        while True:
            try:
                data = await websocket.receive_json()
                
                if data["type"] == "message":
                    mensaje = await chat_service.send_message(
                        message=data["content"],
                        sender_id=user_id,
                        receiver_id=data["receiver_id"],
                        db=db
                    )
                    
                    # Enviar confirmación al remitente
                    await websocket.send_json({
                        "type": "message_sent",
                        "data": {
                            "id": mensaje.id,
                            "timestamp": mensaje.timestamp.isoformat()
                        }
                    })
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        chat_service.disconnect(user_id)
        chat_service.update_user_status(user_id, False, db)

@router.get("/conversaciones", response_model=List[ConversacionResponse])
async def get_conversaciones(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene la lista de conversaciones del usuario"""
    conversaciones = []
    
    # Obtener usuarios con los que ha tenido conversaciones
    if current_user.rol == "abogado":
        usuarios = db.query(Usuario).filter(
            Usuario.rol == "cliente",
            Usuario.id.in_(
                db.query(Mensaje.receptor_id).filter(Mensaje.remitente_id == current_user.id).union(
                    db.query(Mensaje.remitente_id).filter(Mensaje.receptor_id == current_user.id)
                )
            )
        ).all()
    else:
        usuarios = db.query(Usuario).filter(
            Usuario.rol == "abogado",
            Usuario.id.in_(
                db.query(Mensaje.receptor_id).filter(Mensaje.remitente_id == current_user.id).union(
                    db.query(Mensaje.remitente_id).filter(Mensaje.receptor_id == current_user.id)
                )
            )
        ).all()
    
    for usuario in usuarios:
        # Obtener último mensaje
        ultimo_mensaje = db.query(Mensaje).filter(
            ((Mensaje.remitente_id == current_user.id) & (Mensaje.receptor_id == usuario.id)) |
            ((Mensaje.remitente_id == usuario.id) & (Mensaje.receptor_id == current_user.id))
        ).order_by(Mensaje.timestamp.desc()).first()
        
        # Contar mensajes no leídos
        no_leidos = chat_service.get_unread_count(current_user.id, db)
        
        conversaciones.append(ConversacionResponse(
            id=usuario.id,
            nombre=usuario.nombre,
            ultimo_mensaje=ultimo_mensaje.contenido if ultimo_mensaje else None,
            timestamp=ultimo_mensaje.timestamp if ultimo_mensaje else None,
            no_leidos=no_leidos,
            online=usuario.online
        ))
    
    return conversaciones

@router.get("/mensajes/{other_user_id}", response_model=List[MensajeResponse])
async def get_mensajes(
    other_user_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene los mensajes de una conversación específica"""
    return chat_service.get_conversation(current_user.id, other_user_id, db)

@router.post("/mensajes/{message_id}/leer")
async def marcar_mensaje_leido(
    message_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Marca un mensaje como leído"""
    return await chat_service.mark_as_read(message_id, current_user.id, db)

@router.post("/messages", response_model=ChatMessage)
def create_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return ChatService(db).create_message(message, current_user)

@router.get("/messages", response_model=List[ChatMessage])
def get_messages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return ChatService(db).get_messages(current_user, skip, limit)

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    db: Session = Depends(get_db)
):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat") 