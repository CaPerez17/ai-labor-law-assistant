"""
Script de prueba para la búsqueda BM25
------------------------------------
Este script prueba la funcionalidad de búsqueda BM25 utilizando curl.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Asegurarnos de que estamos en el directorio correcto
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# Asegurar que el directorio backend esté en sys.path
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Importar configuración
import config

def test_search(query):
    """Prueba la búsqueda con una consulta específica"""
    url = f"http://{config.HOST}:{config.PORT}/api/search/"
    data = json.dumps({"query": query})
    
    try:
        cmd = [
            "curl", "-X", "POST", url,
            "-H", "Content-Type: application/json",
            "-d", data
        ]
        
        print(f"\nEnviando consulta: '{query}' a {url}")
        print("Comando:", " ".join(cmd))
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("\nRespuesta:")
        try:
            # Formatear bonito el JSON
            formatted_json = json.dumps(json.loads(result.stdout), indent=2, ensure_ascii=False)
            print(formatted_json)
        except json.JSONDecodeError:
            print(result.stdout)
            
        return True
            
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar la consulta: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Prueba de la funcionalidad de búsqueda BM25")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Usar la consulta proporcionada como argumento
        query = sys.argv[1]
    else:
        # Consultas de prueba por defecto
        queries = [
            "¿Cuántos días de licencia de maternidad me corresponden?",
            "¿Cuál es el salario mínimo en Colombia?",
            "¿Qué es el fuero de estabilidad laboral reforzada?",
            "¿Cómo se calcula la indemnización por despido sin justa causa?"
        ]
        
        for query in queries:
            success = test_search(query)
            if not success:
                break
                
    print("\nPruebas completadas.") 