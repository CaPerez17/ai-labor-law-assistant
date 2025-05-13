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

# Conectar a la base de datos
DB_URL="postgresql://legalassista_db_user:YhbZmulvC2eOc2KkUH76rxD19K9AKKNu@dpg-d0alb1ruibrs73a9udv0-a.oregon-postgres.render.com/legalassista_db"
psql "$DB_URL" 