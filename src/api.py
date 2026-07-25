# -*- coding: utf-8 -*-
"""
api.py
------
Etapa 3 del proyecto: expone el agente como un servicio web (FastAPI) para
poder hacer el deploy en OCI Compute y que cualquier persona colaboradora
pueda usarlo desde el navegador, sin instalar nada.

Endpoints:
    GET  /                -> interfaz web simple para probar el agente
    GET  /salud           -> health check (para monitoreo / load balancer)
    POST /api/preguntar   -> {"pregunta": "...", "k": 3} -> respuesta + fuentes

Ejecutar localmente:
    uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
"""

import sys
from pathlib import Path

# Aseguramos que este directorio (src/) esté en el sys.path, sin importar
# desde dónde se invoque uvicorn (necesario para los imports de abajo).
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agente import AgenteClinica  # noqa: E402

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Agente Clínica Vitalis",
    description="Agente de IA que responde preguntas sobre el manual de políticas de la clínica.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# El agente se carga una sola vez al iniciar el servicio (no en cada request).
agente = AgenteClinica(ruta_chunks=str(BASE_DIR / "data" / "chunks.json"))


class Pregunta(BaseModel):
    pregunta: str
    k: int = 3


class Respuesta(BaseModel):
    respuesta: str
    fuentes: list[dict]
    backend: str


@app.get("/salud")
def salud():
    return {"status": "ok", "backend": agente.backend}


@app.post("/api/preguntar", response_model=Respuesta)
def preguntar(payload: Pregunta):
    if not payload.pregunta.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    agente.k = payload.k
    resultado = agente.responder(payload.pregunta)
    return {
        "respuesta": resultado["respuesta"],
        "fuentes": resultado["fuentes"],
        "backend": agente.backend,
    }


@app.get("/", response_class=HTMLResponse)
def index():
    return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")


# Sirve archivos estáticos adicionales (CSS/JS) si se agregan más adelante.
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
