#!/bin/bash

# Iniciar Redis
redis-server &

# Iniciar PostgreSQL (si no está corriendo)
pg_ctl -D /usr/local/var/postgres start

# Iniciar Backend
cd backend/app
./scripts/run_dev.sh &

# Iniciar WebSocket
cd backend/app
./scripts/run_websocket.sh &

# Iniciar Frontend
cd frontend
./scripts/run_dev.sh &

# Iniciar Stripe Webhook
stripe listen --forward-to localhost:8000/api/v1/pagos/webhook &

echo "Todos los servicios han sido iniciados"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "WebSocket: ws://localhost:8000/ws"
echo "Stripe Webhook: Escuchando en localhost:8000/api/v1/pagos/webhook" 