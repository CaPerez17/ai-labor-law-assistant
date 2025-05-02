#!/bin/bash

# Activar el entorno virtual (si existe)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instalar dependencias si es necesario
pip install -r requirements.txt

# Ejecutar migraciones si es necesario
if command -v alembic &> /dev/null; then
    alembic upgrade head
fi

# Inicializar datos de prueba si es necesario
python -c "
import os
try:
    from app.db.session import SessionLocal
    from app.scripts.init_test_data import init_test_data
    db = SessionLocal()
    init_test_data(db)
    db.close()
    print('Datos de prueba inicializados correctamente')
except Exception as e:
    print(f'No se pudieron inicializar los datos de prueba: {str(e)}')
"

# Iniciar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 