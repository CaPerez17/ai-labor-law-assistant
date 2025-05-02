#!/bin/bash

# Colores para facilitar la lectura
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================${NC}"
echo -e "${BLUE}   INICIANDO ENTORNO DE PRUEBA DE LEGALASSISTA${NC}"
echo -e "${BLUE}========================================================${NC}"

# Verificar prerrequisitos
echo -e "\n${YELLOW}[1/7]${NC} Verificando prerrequisitos..."

# Python
python_version=$(python --version 2>&1)
if [[ $python_version == *"Python 3"* ]]; then
  echo -e "  ${GREEN}✓${NC} Python: $python_version"
else
  echo -e "  ${RED}✗${NC} Python 3.8+ requerido. Versión detectada: $python_version"
  exit 1
fi

# Node.js
if command -v node &> /dev/null; then
  node_version=$(node --version)
  echo -e "  ${GREEN}✓${NC} Node.js: $node_version"
else
  echo -e "  ${RED}✗${NC} Node.js no encontrado"
  exit 1
fi

# PostgreSQL
if pg_isready &> /dev/null; then
  echo -e "  ${GREEN}✓${NC} PostgreSQL está corriendo"
else
  echo -e "  ${YELLOW}!${NC} Iniciando PostgreSQL..."
  pg_ctl -D /usr/local/var/postgres start
  
  # Verificar nuevamente
  if pg_isready &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} PostgreSQL iniciado correctamente"
  else
    echo -e "  ${RED}✗${NC} No se pudo iniciar PostgreSQL"
    exit 1
  fi
fi

# Redis
if command -v redis-cli &> /dev/null && redis-cli ping &> /dev/null; then
  echo -e "  ${GREEN}✓${NC} Redis está corriendo"
else
  echo -e "  ${YELLOW}!${NC} Iniciando Redis..."
  redis-server &
  sleep 2
  
  # Verificar nuevamente
  if redis-cli ping &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Redis iniciado correctamente"
  else
    echo -e "  ${RED}✗${NC} No se pudo iniciar Redis"
    exit 1
  fi
fi

# Stripe CLI
if command -v stripe &> /dev/null; then
  stripe_version=$(stripe --version)
  echo -e "  ${GREEN}✓${NC} Stripe CLI: $stripe_version"
else
  echo -e "  ${RED}✗${NC} Stripe CLI no encontrado. Instálalo desde https://stripe.com/docs/stripe-cli"
  exit 1
fi

# Verificar archivos .env
echo -e "\n${YELLOW}[2/7]${NC} Verificando archivos de configuración..."

if [ -f "backend/app/.env" ]; then
  echo -e "  ${GREEN}✓${NC} Archivo backend/app/.env encontrado"
else
  echo -e "  ${YELLOW}!${NC} Creando archivo backend/app/.env desde ejemplo"
  cp backend/app/.env.example backend/app/.env
  echo -e "  ${YELLOW}!${NC} Por favor edita backend/app/.env con tus credenciales"
fi

if [ -f "frontend/.env" ]; then
  echo -e "  ${GREEN}✓${NC} Archivo frontend/.env encontrado"
else
  echo -e "  ${YELLOW}!${NC} Creando archivo frontend/.env desde ejemplo"
  cp frontend/.env.example frontend/.env
  echo -e "  ${YELLOW}!${NC} Por favor edita frontend/.env con tus credenciales"
fi

# Dar permisos de ejecución a los scripts
echo -e "\n${YELLOW}[3/7]${NC} Configurando permisos de ejecución para scripts..."
chmod +x backend/app/scripts/run_dev.sh
chmod +x backend/app/scripts/run_websocket.sh
chmod +x frontend/scripts/run_dev.sh
echo -e "  ${GREEN}✓${NC} Permisos actualizados"

# Iniciar Backend
echo -e "\n${YELLOW}[4/7]${NC} Iniciando Backend FastAPI..."
cd backend/app
./scripts/run_dev.sh &
BACKEND_PID=$!
cd ../../
echo -e "  ${GREEN}✓${NC} Backend iniciado (PID: $BACKEND_PID)"
echo -e "  ${BLUE}ℹ${NC} API disponible en: http://localhost:8000/docs"

# Esperar a que el backend esté listo
echo -e "  ${YELLOW}!${NC} Esperando a que el backend esté disponible..."
sleep 5

# Iniciar WebSocket
echo -e "\n${YELLOW}[5/7]${NC} Iniciando servicio WebSocket..."
cd backend/app
./scripts/run_websocket.sh &
WEBSOCKET_PID=$!
cd ../../
echo -e "  ${GREEN}✓${NC} WebSocket iniciado (PID: $WEBSOCKET_PID)"
echo -e "  ${BLUE}ℹ${NC} WebSocket disponible en: ws://localhost:8000/ws"

# Iniciar Frontend
echo -e "\n${YELLOW}[6/7]${NC} Iniciando Frontend Next.js..."
cd frontend
./scripts/run_dev.sh &
FRONTEND_PID=$!
cd ..
echo -e "  ${GREEN}✓${NC} Frontend iniciado (PID: $FRONTEND_PID)"
echo -e "  ${BLUE}ℹ${NC} Frontend disponible en: http://localhost:3000"

# Iniciar Stripe Webhook
echo -e "\n${YELLOW}[7/7]${NC} Iniciando Stripe Webhook..."
stripe listen --forward-to localhost:8000/api/v1/pagos/webhook &
STRIPE_PID=$!
echo -e "  ${GREEN}✓${NC} Stripe Webhook iniciado (PID: $STRIPE_PID)"
echo -e "  ${BLUE}ℹ${NC} Webhook disponible en: http://localhost:8000/api/v1/pagos/webhook"

# Mostrar información de usuarios y flujos
echo -e "\n${BLUE}========================================================${NC}"
echo -e "${BLUE}   ENTORNO DE PRUEBA LISTO${NC}"
echo -e "${BLUE}========================================================${NC}"

echo -e "\n${YELLOW}USUARIOS DEMO:${NC}"
echo -e "  ${BLUE}➤ Admin:${NC} admin@legalassista.com / Admin123!"
echo -e "  ${BLUE}➤ Abogado:${NC} abogado@legalassista.com / Abogado123!"
echo -e "  ${BLUE}➤ Cliente:${NC} cliente@legalassista.com / Cliente123!"

echo -e "\n${YELLOW}FLUJOS DE PRUEBA:${NC}"
echo -e "  ${BLUE}1. Flujo de Cliente:${NC}"
echo -e "     - Registro/Login como cliente"
echo -e "     - Completar onboarding conversacional"
echo -e "     - Crear caso"
echo -e "     - Analizar contrato/documento"
echo -e "     - Realizar pago (Stripe sandbox)"
echo -e "     - Chatear con abogado"

echo -e "  ${BLUE}2. Flujo de Abogado:${NC}"
echo -e "     - Login como abogado"
echo -e "     - Ver casos asignados"
echo -e "     - Responder mensajes"
echo -e "     - Actualizar estado de casos"

echo -e "  ${BLUE}3. Flujo de Admin:${NC}"
echo -e "     - Login como admin"
echo -e "     - Gestionar usuarios"
echo -e "     - Ver analytics"

echo -e "\n${YELLOW}SERVICIOS INICIADOS:${NC}"
echo -e "  ${BLUE}➤ Backend:${NC} http://localhost:8000/docs (PID: $BACKEND_PID)"
echo -e "  ${BLUE}➤ Frontend:${NC} http://localhost:3000 (PID: $FRONTEND_PID)"
echo -e "  ${BLUE}➤ WebSocket:${NC} ws://localhost:8000/ws (PID: $WEBSOCKET_PID)"
echo -e "  ${BLUE}➤ Stripe Webhook:${NC} http://localhost:8000/api/v1/pagos/webhook (PID: $STRIPE_PID)"

echo -e "\n${YELLOW}PARA DETENER TODOS LOS SERVICIOS:${NC}"
echo -e "  Presiona CTRL+C o ejecuta: kill $BACKEND_PID $WEBSOCKET_PID $FRONTEND_PID $STRIPE_PID"

# Esperar a que el usuario presione CTRL+C
trap "echo -e '\n${RED}Deteniendo todos los servicios...${NC}'; kill $BACKEND_PID $WEBSOCKET_PID $FRONTEND_PID $STRIPE_PID; echo -e '${GREEN}Servicios detenidos${NC}'; exit" INT
echo -e "\n${YELLOW}Presiona CTRL+C para detener todos los servicios${NC}"
wait 