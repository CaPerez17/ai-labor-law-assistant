"""
Gestor de conexiones WebSocket
----------------------------
"""

from typing import List, Dict
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Gestor de conexiones WebSocket"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int = None):
        """Acepta una nueva conexión WebSocket"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            self.user_connections[user_id] = websocket
            
        logger.info(f"Nueva conexión WebSocket establecida. Usuario: {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int = None):
        """Desconecta un WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
            
        logger.info(f"Conexión WebSocket cerrada. Usuario: {user_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Envía un mensaje a una conexión específica"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error enviando mensaje personal: {e}")

    async def send_message_to_user(self, message: str, user_id: int):
        """Envía un mensaje a un usuario específico"""
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error enviando mensaje a usuario {user_id}: {e}")
                # Limpiar conexión si hay error
                self.disconnect(websocket, user_id)

    async def broadcast(self, message: str):
        """Envía un mensaje a todas las conexiones activas"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error en broadcast: {e}")
                disconnected.append(connection)
        
        # Limpiar conexiones desconectadas
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection) 