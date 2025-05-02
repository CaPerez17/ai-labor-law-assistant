from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LegalAssista Simple API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a LegalAssista!"}

@app.get("/users")
def get_users():
    return [
        {"id": 1, "email": "admin@legalassista.com", "role": "admin"},
        {"id": 2, "email": "abogado@legalassista.com", "role": "abogado"},
        {"id": 3, "email": "cliente@legalassista.com", "role": "cliente"}
    ] 