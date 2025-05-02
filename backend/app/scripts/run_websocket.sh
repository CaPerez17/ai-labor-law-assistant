#!/bin/bash

# Activar el entorno virtual (si existe)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Verificar que Redis esté funcionando
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "Redis está funcionando correctamente"
    else
        echo "Redis no está respondiendo. Intentando iniciar..."
        redis-server &
        sleep 2
        if redis-cli ping &> /dev/null; then
            echo "Redis iniciado correctamente"
        else
            echo "Error: No se pudo iniciar Redis. El WebSocket puede no funcionar correctamente."
        fi
    fi
else
    echo "Advertencia: Redis no está instalado. El WebSocket puede no funcionar correctamente."
fi

# Iniciar el servicio de WebSocket
echo "Iniciando servicio WebSocket..."
if [ -f "app/websocket/main.py" ]; then
    python -m app.websocket.main
else
    echo "Error: No se encontró el módulo WebSocket (app/websocket/main.py)"
    echo "Creando un servicio WebSocket básico..."
    
    mkdir -p app/websocket
    
    cat > app/websocket/main.py << 'EOF'
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Estructura para mantener las conexiones activas por caso
class ConnectionManager:
    def __init__(self):
        # {caso_id: [conexiones]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, caso_id: int):
        await websocket.accept()
        if caso_id not in self.active_connections:
            self.active_connections[caso_id] = []
        self.active_connections[caso_id].append(websocket)
        logger.info(f"Cliente conectado al caso {caso_id}. Total conexiones: {len(self.active_connections[caso_id])}")

    def disconnect(self, websocket: WebSocket, caso_id: int):
        if caso_id in self.active_connections:
            self.active_connections[caso_id].remove(websocket)
            logger.info(f"Cliente desconectado del caso {caso_id}. Conexiones restantes: {len(self.active_connections[caso_id])}")

    async def broadcast(self, message: str, caso_id: int):
        if caso_id in self.active_connections:
            for connection in self.active_connections[caso_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error al enviar mensaje: {str(e)}")


manager = ConnectionManager()

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
    uvicorn.run("app.websocket.main:app", host="0.0.0.0", port=8001, reload=True)
EOF

    # Iniciar el servicio WebSocket básico
    python -m app.websocket.main
fi 