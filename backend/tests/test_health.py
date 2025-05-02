from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

client = TestClient(app)

def test_health():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 