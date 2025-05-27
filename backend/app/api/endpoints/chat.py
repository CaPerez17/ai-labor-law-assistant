from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.usuario import Usuario
from app.models.mensaje import Mensaje
from app.schemas.chat import MensajeCreate, MensajeResponse, ConversacionResponse
from app.services.chat_service import ChatService
from app.core.websocket import ConnectionManager

router = APIRouter()
chat_service = ChatService()
manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    try:
        await manager.connect(websocket, user_id)
        
        while True:
            try:
                data = await websocket.receive_json()
                
                if data["type"] == "message":
                    # Crear mensaje en la base de datos
                    mensaje = Mensaje(
                        contenido=data["content"],
                        remitente_id=user_id,
                        receptor_id=data["receiver_id"]
                    )
                    db.add(mensaje)
                    db.commit()
                    db.refresh(mensaje)
                    
                    # Enviar confirmación al remitente
                    await websocket.send_json({
                        "type": "message_sent",
                        "data": {
                            "id": mensaje.id,
                            "timestamp": mensaje.timestamp.isoformat()
                        }
                    })
                    
                    # Enviar mensaje al receptor si está conectado
                    await manager.send_message_to_user(
                        f"Nuevo mensaje de {user_id}: {data['content']}", 
                        data["receiver_id"]
                    )
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        print(f"Error en WebSocket: {e}")
    finally:
        manager.disconnect(websocket, user_id)

@router.get("/conversaciones", response_model=List[ConversacionResponse])
async def get_conversaciones(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene la lista de conversaciones del usuario"""
    conversaciones = []
    
    # Obtener usuarios con los que ha tenido conversaciones
    if current_user.rol.value == "ABOGADO":
        usuarios = db.query(Usuario).filter(
            Usuario.rol.value == "CLIENTE"
        ).all()
    else:
        usuarios = db.query(Usuario).filter(
            Usuario.rol.value == "ABOGADO"
        ).all()
    
    for usuario in usuarios:
        # Obtener último mensaje
        ultimo_mensaje = db.query(Mensaje).filter(
            ((Mensaje.remitente_id == current_user.id) & (Mensaje.receptor_id == usuario.id)) |
            ((Mensaje.remitente_id == usuario.id) & (Mensaje.receptor_id == current_user.id))
        ).order_by(Mensaje.timestamp.desc()).first()
        
        # Contar mensajes no leídos
        no_leidos = db.query(Mensaje).filter(
            Mensaje.remitente_id == usuario.id,
            Mensaje.receptor_id == current_user.id,
            Mensaje.leido == False
        ).count()
        
        conversaciones.append(ConversacionResponse(
            id=usuario.id,
            nombre=usuario.nombre,
            ultimo_mensaje=ultimo_mensaje.contenido if ultimo_mensaje else None,
            timestamp=ultimo_mensaje.timestamp if ultimo_mensaje else None,
            no_leidos=no_leidos,
            online=False  # Implementar lógica de estado online si es necesario
        ))
    
    return conversaciones

@router.get("/mensajes/{other_user_id}", response_model=List[MensajeResponse])
async def get_mensajes(
    other_user_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene los mensajes de una conversación específica"""
    mensajes = db.query(Mensaje).filter(
        ((Mensaje.remitente_id == current_user.id) & (Mensaje.receptor_id == other_user_id)) |
        ((Mensaje.remitente_id == other_user_id) & (Mensaje.receptor_id == current_user.id))
    ).order_by(Mensaje.timestamp.asc()).all()
    
    return mensajes

@router.post("/mensajes/{message_id}/leer")
async def marcar_mensaje_leido(
    message_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Marca un mensaje como leído"""
    mensaje = db.query(Mensaje).filter(
        Mensaje.id == message_id,
        Mensaje.receptor_id == current_user.id
    ).first()
    
    if mensaje:
        mensaje.leido = True
        db.commit()
        return {"message": "Mensaje marcado como leído"}
    else:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")

@router.post("/mensajes", response_model=MensajeResponse)
def create_message(
    message: MensajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crea un nuevo mensaje"""
    db_mensaje = Mensaje(
        contenido=message.contenido,
        remitente_id=current_user.id,
        receptor_id=message.receptor_id
    )
    
    db.add(db_mensaje)
    db.commit()
    db.refresh(db_mensaje)
    
    return db_mensaje 