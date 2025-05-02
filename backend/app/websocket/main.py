from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict, Optional
import json
import asyncio
import logging
import redis.asyncio as redis
import os
from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Estructura para mantener las conexiones activas por caso
class ConnectionManager:
    def __init__(self):
        # {caso_id: [conexiones]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.redis: Optional[redis.Redis] = None
        self.pubsub = None
        self.redis_task = None

    async def setup_redis(self):
        try:
            self.redis = await redis.from_url(settings.REDIS_URL)
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe("chat_messages")
            self.redis_task = asyncio.create_task(self.redis_listener())
            logger.info("Redis PubSub configurado correctamente")
        except Exception as e:
            logger.error(f"Error al configurar Redis: {str(e)}")
            logger.warning("Continuando sin soporte Redis - las notificaciones sólo funcionarán en la misma instancia")

    async def redis_listener(self):
        """Escucha mensajes de Redis y los distribuye a las conexiones WebSocket"""
        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    caso_id = data.get("caso_id")
                    if caso_id:
                        # Evita un loop enviando solo a las conexiones locales
                        await self.broadcast_local(json.dumps(data["message"]), caso_id)
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Error en el listener de Redis: {str(e)}")
        finally:
            if self.pubsub:
                await self.pubsub.unsubscribe("chat_messages")

    async def connect(self, websocket: WebSocket, caso_id: int):
        await websocket.accept()
        if caso_id not in self.active_connections:
            self.active_connections[caso_id] = []
        self.active_connections[caso_id].append(websocket)
        logger.info(f"Cliente conectado al caso {caso_id}. Total conexiones: {len(self.active_connections[caso_id])}")

    def disconnect(self, websocket: WebSocket, caso_id: int):
        if caso_id in self.active_connections:
            try:
                self.active_connections[caso_id].remove(websocket)
                logger.info(f"Cliente desconectado del caso {caso_id}. Conexiones restantes: {len(self.active_connections[caso_id])}")
            except ValueError:
                pass  # Ya fue removido

    async def broadcast_local(self, message: str, caso_id: int):
        """Envía un mensaje sólo a las conexiones locales"""
        if caso_id in self.active_connections:
            disconnected = []
            for i, connection in enumerate(self.active_connections[caso_id]):
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error al enviar mensaje: {str(e)}")
                    disconnected.append(i)
            
            # Limpiar conexiones desconectadas
            for i in sorted(disconnected, reverse=True):
                try:
                    del self.active_connections[caso_id][i]
                except:
                    pass

    async def broadcast(self, message: str, caso_id: int):
        """Publica el mensaje a Redis para distribuirlo a todas las instancias"""
        try:
            # Primero enviamos a las conexiones locales
            await self.broadcast_local(message, caso_id)
            
            # Luego publicamos a Redis para otras instancias
            if self.redis:
                msg_data = {
                    "caso_id": caso_id,
                    "message": json.loads(message) if isinstance(message, str) else message
                }
                await self.redis.publish("chat_messages", json.dumps(msg_data))
        except Exception as e:
            logger.error(f"Error en broadcast: {str(e)}")


manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    await manager.setup_redis()

@app.on_event("shutdown")
async def shutdown_event():
    if manager.redis:
        await manager.redis.close()
    if manager.redis_task:
        manager.redis_task.cancel()

@app.websocket("/ws/chat/{caso_id}")
async def websocket_endpoint(websocket: WebSocket, caso_id: int):
    await manager.connect(websocket, caso_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Procesamos el mensaje recibido
            try:
                message_data = json.loads(data)
                # Aquí podríamos guardar el mensaje en la base de datos
                logger.info(f"Mensaje recibido en caso {caso_id}: {message_data}")
                
                # Reenviamos el mensaje a todos los clientes conectados al mismo caso
                await manager.broadcast(data, caso_id)
            except json.JSONDecodeError:
                logger.error(f"Error al decodificar JSON: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, caso_id)
        # Notificamos a los demás clientes que este usuario se desconectó
        await manager.broadcast(
            json.dumps({"type": "system", "content": "Un usuario se ha desconectado"}),
            caso_id
        )
    except Exception as e:
        logger.error(f"Error en WebSocket: {str(e)}")
        manager.disconnect(websocket, caso_id)

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor WebSocket...")
    port = int(os.environ.get("WS_PORT", "8001"))
    uvicorn.run("app.websocket.main:app", host="0.0.0.0", port=port, reload=False) 