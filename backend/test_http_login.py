#!/usr/bin/env python3
"""
Script para probar el login via HTTP
"""
import requests
import json
import time
import subprocess
import sys
from threading import Thread

def start_server():
    """Inicia el servidor en un hilo separado"""
    import os
    os.chdir("/Users/camilope/ai-labor-law-assistant/backend")
    os.environ["PYTHONPATH"] = "/Users/camilope/ai-labor-law-assistant/backend"
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8001"
    ])

def test_login_endpoint():
    """Prueba el endpoint de login vía HTTP"""
    base_url = "http://localhost:8001"
    
    # Datos de login
    login_data = {
        "username": "abogado@legalassista.com",
        "password": "Abogado123!"
    }
    
    print("🔍 Probando endpoint de login...")
    
    try:
        # Verificar que el servidor esté disponible
        print("1. Verificando servidor...")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   - Health check: {health_response.status_code}")
        
        # Probar login
        print("2. Enviando petición de login...")
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            data=login_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=10
        )
        
        print(f"   - Status code: {login_response.status_code}")
        print(f"   - Headers: {dict(login_response.headers)}")
        
        if login_response.status_code == 200:
            result = login_response.json()
            print("✅ Login exitoso!")
            print(f"   - Token: {result.get('access_token', 'N/A')[:20]}...")
            print(f"   - Usuario: {result.get('user', {}).get('email', 'N/A')}")
            print(f"   - Rol: {result.get('user', {}).get('role', 'N/A')}")
            return True
        else:
            print(f"❌ Login falló:")
            print(f"   - Código: {login_response.status_code}")
            print(f"   - Respuesta: {login_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando servidor de prueba...")
    
    # Iniciar servidor en hilo separado
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Esperar a que el servidor inicie
    print("⏳ Esperando a que el servidor inicie...")
    time.sleep(8)
    
    # Probar login
    success = test_login_endpoint()
    
    if success:
        print("\n🎉 ¡Test HTTP exitoso!")
    else:
        print("\n💥 ¡Test HTTP falló!")
    
    print("\n⚠️  Para detener el servidor, presiona Ctrl+C") 