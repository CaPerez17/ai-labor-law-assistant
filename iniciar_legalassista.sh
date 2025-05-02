#!/bin/bash

echo "🚀 Iniciando LegalAssista..."

# Matar procesos anteriores
echo "🧹 Limpiando procesos anteriores..."
pkill -f "uvicorn main:app"
pkill -f "node.*vite"

# Iniciar el backend
echo "🔧 Iniciando el backend..."
cd backend/app
python -m uvicorn main:app --reload &
BACKEND_PID=$!
cd ../..

# Esperar un momento
echo "⏳ Esperando a que el backend esté listo..."
sleep 5

# Iniciar el frontend
echo "🎨 Iniciando el frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Servicios iniciados:"
echo "   Backend: http://localhost:8000/docs (PID: $BACKEND_PID)"
echo "   Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"

echo "👤 Usuarios de prueba:"
echo "   Admin: admin@legalassista.com / Admin123!"
echo "   Abogado: abogado@legalassista.com / Abogado123!"
echo "   Cliente: cliente@legalassista.com / Cliente123!"

echo "🛑 Para detener los servicios: kill $BACKEND_PID $FRONTEND_PID"

# Mantener el script en ejecución
wait 