FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias necesarias para paquetes Python
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Hacer ejecutable el script de inicio
RUN chmod +x start.sh

# Exponer puerto
EXPOSE 8000

# Establecer comando para iniciar la aplicación
CMD ["./start.sh"] 