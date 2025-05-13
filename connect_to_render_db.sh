#!/bin/bash

# Script para conectarse a PostgreSQL de Render
echo "Verificando instalación de psql..."
if ! command -v psql &> /dev/null; then
    echo "psql no está instalado. Instalalo con:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "  macOS: brew install postgresql"
    exit 1
fi

echo "Conectando a la base de datos PostgreSQL en Render..."
echo "Usar los siguientes comandos una vez conectado:"
echo "  \\dt                       → listar tablas"
echo "  \\d <table_name>           → describir tabla"
echo "  SELECT * FROM usuarios LIMIT 10;  → ver primeros 10 usuarios"
echo "  \\q                        → salir"
echo ""

# Solicitar URL de conexión segura
echo "Por favor, introduce la URL de conexión PostgreSQL (no se mostrará en pantalla):"
read -s DB_URL

if [ -z "$DB_URL" ]; then
    echo "Error: No se proporcionó ninguna URL de conexión."
    echo "La URL debe tener el formato: postgresql://usuario:contraseña@host:puerto/nombre_db"
    exit 1
fi

# Conectar a la base de datos
psql "$DB_URL" 