from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Test API",
    description="Prueba simple para verificar FastAPI",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta raíz
@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "API de prueba funcionando correctamente",
    }

# Ruta para verificar estado de salud
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Punto de entrada
if __name__ == "__main__":
    uvicorn.run("test_run:app", host="0.0.0.0", port=8005, reload=True) 