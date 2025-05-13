#!/bin/bash

# Script para inicializar usuarios en la base de datos de producción en Render

echo "Iniciando proceso de creación de usuarios en base de datos de producción"

# URL del backend de Render
BACKEND_URL="https://legalassista-backend.onrender.com"

# Intenta obtener información de salud del backend
echo "Verificando conexión con el backend en $BACKEND_URL/api/health"
HEALTH_CHECK=$(curl -s "$BACKEND_URL/api/health")
echo "Respuesta: $HEALTH_CHECK"

# Crear usuarios directamente mediante API
echo "Creando usuario admin..."
curl -X POST "$BACKEND_URL/api/auth/create-admin" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@legalassista.com","password":"admin123","nombre":"Administrador"}'

echo "Creando usuario abogado..."
curl -X POST "$BACKEND_URL/api/auth/create-lawyer" \
  -H "Content-Type: application/json" \
  -d '{"email":"abogado@legalassista.com","password":"abogado123","nombre":"Abogado"}'

echo "Creando usuario cliente..."
curl -X POST "$BACKEND_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"cliente@legalassista.com","password":"cliente123","nombre":"Cliente"}'

echo "Proceso de creación de usuarios completado" 