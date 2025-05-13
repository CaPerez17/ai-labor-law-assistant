#!/usr/bin/env python3
"""
Script para probar específicamente la autenticación OAuth2 y FastAPI
-------------------------------------------------------------------
Este script emula una solicitud de login similar a lo que haría un cliente
usando OAuth2PasswordRequestForm, que es lo que FastAPI espera para autenticación.
"""

import os
import sys
import requests
import json
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL del backend
DEFAULT_URL = "https://legalassista.onrender.com"
BACKEND_URL = os.environ.get("BACKEND_URL", DEFAULT_URL)

def test_oauth_login(email, password):
    """
    Prueba la autenticación OAuth2 con FastAPI.
    
    Args:
        email: Correo electrónico del usuario
        password: Contraseña del usuario
    """
    # Endpoints a probar
    login_endpoints = [
        f"{BACKEND_URL}/api/auth/login",  # Endpoint principal
        f"{BACKEND_URL}/api/login",       # Posible alternativa
        f"{BACKEND_URL}/auth/login"       # Otra alternativa
    ]
    
    # Métodos de autenticación a probar
    login_methods = [
        # Método 1: FormData (esperado por OAuth2)
        {
            "description": "FormData (estándar OAuth2)",
            "data": {
                "username": email,  # OAuth2 espera 'username', no 'email'
                "password": password
            },
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "is_json": False
        },
        # Método 2: JSON con estructura username/password
        {
            "description": "JSON con username/password",
            "data": {
                "username": email,
                "password": password
            },
            "headers": {
                "Content-Type": "application/json"
            },
            "is_json": True
        },
        # Método 3: JSON con estructura email/password
        {
            "description": "JSON con email/password",
            "data": {
                "email": email,
                "password": password
            },
            "headers": {
                "Content-Type": "application/json"
            },
            "is_json": True
        }
    ]
    
    # Probar todas las combinaciones
    for endpoint in login_endpoints:
        logger.info(f"\n=== Probando endpoint: {endpoint} ===")
        
        for method in login_methods:
            logger.info(f"\n-- Método: {method['description']} --")
            
            try:
                # Preparar datos según el método
                if method["is_json"]:
                    response = requests.post(
                        endpoint,
                        json=method["data"],
                        headers=method["headers"]
                    )
                else:
                    response = requests.post(
                        endpoint,
                        data=method["data"],
                        headers=method["headers"]
                    )
                
                # Log de la respuesta
                logger.info(f"Status code: {response.status_code}")
                logger.info(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
                
                if 200 <= response.status_code < 300:
                    logger.info(f"Respuesta exitosa: {json.dumps(response.json(), indent=2)}")
                    return True
                else:
                    logger.warning(f"Respuesta fallida: {response.text}")
            
            except Exception as e:
                logger.error(f"Error en la solicitud: {str(e)}")
    
    logger.error("⚠️ Todas las combinaciones de autenticación fallaron")
    return False

if __name__ == "__main__":
    # Solicitar credenciales por línea de comandos
    if len(sys.argv) < 3:
        print("Uso: python test_oauth.py <email> <password>")
        print("Ejemplo: python test_oauth.py admin@legalassista.com admin123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    logger.info(f"Probando autenticación para: {email}")
    logger.info(f"URL del backend: {BACKEND_URL}")
    
    if test_oauth_login(email, password):
        logger.info("✅ Autenticación exitosa en al menos un método")
    else:
        logger.error("❌ Autenticación fallida en todos los métodos") 