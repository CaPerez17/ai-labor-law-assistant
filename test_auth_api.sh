#!/bin/bash

# Script para probar la API de autenticación del backend

echo "Probando API de autenticación en LegalAssista"

# URL del backend
BACKEND_URL="https://legalassista-backend.onrender.com"

# Verificar que el backend esté accesible
echo "Verificando estado del backend..."
curl -s "$BACKEND_URL/api/health"
echo ""

# Probar login con usuario administrador
echo "Probando login con admin@legalassista.com..."
curl -v -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@legalassista.com","password":"admin123"}'
echo ""

# Probar login con usuario cliente
echo "Probando login con cliente@legalassista.com..."
curl -v -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"cliente@legalassista.com","password":"cliente123"}'
echo ""

echo "Pruebas completadas" 