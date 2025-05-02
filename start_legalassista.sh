#!/bin/bash

# Colores para mejor legibilidad
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================"
echo -e "   INICIANDO ENTORNO DE PRUEBA DE LEGALASSISTA"
echo -e "========================================================${NC}"

# Dar permisos de ejecución a los scripts
echo -e "\n${YELLOW}Configurando permisos de scripts...${NC}"
chmod +x backend/app/scripts/run_dev.sh
chmod +x backend/app/scripts/run_websocket.sh
chmod +x frontend/scripts/run_dev.sh

# Verificar PostgreSQL
echo -e "\n${YELLOW}Verificando PostgreSQL...${NC}"
if pg_isready &> /dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL está ejecutándose"
else
    echo -e "${YELLOW}!${NC} Iniciando PostgreSQL..."
    pg_ctl -D /usr/local/var/postgres start || echo -e "${RED}✗${NC} No se pudo iniciar PostgreSQL"
fi

# Verificar Redis
echo -e "\n${YELLOW}Verificando Redis...${NC}"
if command -v redis-cli &> /dev/null && redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓${NC} Redis está ejecutándose"
else
    echo -e "${YELLOW}!${NC} Iniciando Redis..."
    redis-server &
    sleep 2
fi

# Iniciar Backend
echo -e "\n${YELLOW}Iniciando Backend...${NC}"
cd backend/app
./scripts/run_dev.sh &
BACKEND_PID=$!
cd ../../
echo -e "${GREEN}✓${NC} Backend iniciado (PID: $BACKEND_PID)"

# Esperar a que el backend esté disponible
echo -e "${YELLOW}Esperando a que el backend esté disponible...${NC}"
sleep 10

# Iniciar WebSocket
echo -e "\n${YELLOW}Iniciando WebSocket...${NC}"
cd backend/app
./scripts/run_websocket.sh &
WEBSOCKET_PID=$!
cd ../../
echo -e "${GREEN}✓${NC} WebSocket iniciado (PID: $WEBSOCKET_PID)"

# Iniciar Frontend
echo -e "\n${YELLOW}Iniciando Frontend...${NC}"
cd frontend
./scripts/run_dev.sh &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓${NC} Frontend iniciado (PID: $FRONTEND_PID)"

# Iniciar Stripe Webhook (si Stripe CLI está instalado)
echo -e "\n${YELLOW}Verificando Stripe CLI...${NC}"
if command -v stripe &> /dev/null; then
    echo -e "${YELLOW}Iniciando Stripe Webhook...${NC}"
    stripe listen --forward-to localhost:8000/api/v1/pagos/webhook &
    STRIPE_PID=$!
    echo -e "${GREEN}✓${NC} Stripe Webhook iniciado (PID: $STRIPE_PID)"
else
    echo -e "${YELLOW}!${NC} Stripe CLI no encontrado. El webhook no estará disponible."
    STRIPE_PID=""
fi

# Información final
echo -e "\n${BLUE}========================================================"
echo -e "   ENTORNO DE PRUEBA LISTO"
echo -e "========================================================${NC}"

echo -e "\n${YELLOW}SERVICIOS DISPONIBLES:${NC}"
echo -e "  ${BLUE}➤ Backend API:${NC} http://localhost:8000/docs"
echo -e "  ${BLUE}➤ Frontend:${NC} http://localhost:3000"
echo -e "  ${BLUE}➤ WebSocket:${NC} ws://localhost:8000/ws"
if [ ! -z "$STRIPE_PID" ]; then
    echo -e "  ${BLUE}➤ Stripe Webhook:${NC} http://localhost:8000/api/v1/pagos/webhook"
fi

echo -e "\n${YELLOW}USUARIOS DE PRUEBA:${NC}"
echo -e "  ${BLUE}➤ Admin:${NC} admin@legalassista.com / Admin123!"
echo -e "  ${BLUE}➤ Abogado:${NC} abogado@legalassista.com / Abogado123!"
echo -e "  ${BLUE}➤ Cliente:${NC} cliente@legalassista.com / Cliente123!"

echo -e "\n${YELLOW}PARA DETENER TODOS LOS SERVICIOS:${NC}"
if [ ! -z "$STRIPE_PID" ]; then
    echo -e "  Presiona CTRL+C o ejecuta: kill $BACKEND_PID $WEBSOCKET_PID $FRONTEND_PID $STRIPE_PID"
else
    echo -e "  Presiona CTRL+C o ejecuta: kill $BACKEND_PID $WEBSOCKET_PID $FRONTEND_PID"
fi

# Esperar a que el usuario presione CTRL+C
trap "echo -e '\n${RED}Deteniendo todos los servicios...${NC}'; kill $BACKEND_PID $WEBSOCKET_PID $FRONTEND_PID $STRIPE_PID 2>/dev/null; echo -e '${GREEN}Servicios detenidos${NC}'; exit" INT
echo -e "\n${YELLOW}Presiona CTRL+C para detener todos los servicios${NC}"
wait 