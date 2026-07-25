# Agente de IA — Clínica Vitalis

Agente de inteligencia artificial que responde preguntas sobre el manual de
políticas internas de una clínica de salud (privacidad de datos, turnos,
cancelaciones, convenios y coberturas, instrucciones pre/post consulta), en
lenguaje natural y sin que nadie tenga que abrir el PDF.

Proyecto de punta a punta: **documento → agente → deploy en la nube (OCI)**.

## Demo

- **URL pública (OCI):** `http://<IP-PUBLICA>:8000` ← completar después del deploy (ver `DEPLOY_OCI.md`)
- Captura de pantalla: `docs/screenshot-deploy.png` ← agregar luego del deploy

## Arquitectura

```
                    ┌────────────────────────┐
  politicas.pdf ───▶│  ingest.py (Etapa 1)    │  pypdf + LangChain TextSplitter
                    │  extrae y trocea el PDF │  -> data/chunks.json
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
   pregunta ───────▶│  retriever.py           │  TF-IDF + similitud coseno
                    │  busca los chunks       │  (scikit-learn, 100% offline)
                    │  más relevantes         │
                    └───────────┬─────────────┘
                                │  contexto recuperado
                    ┌───────────▼─────────────┐
                    │  agente.py (Etapa 2)    │  arma el prompt y llama al LLM
                    │  Anthropic / OpenAI /   │  elegido (o modo "mock" sin key)
                    │  Gemini / Cohere / mock │
                    └───────────┬─────────────┘
                                │  respuesta + página fuente
                    ┌───────────▼─────────────┐
                    │  api.py (Etapa 3)       │  FastAPI: /api/preguntar, /salud
                    │  static/index.html      │  interfaz de chat en el navegador
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Docker + OCI Compute   │  deploy público (ver DEPLOY_OCI.md)
                    └─────────────────────────┘
```

**Por qué estas decisiones:**
- **TF-IDF en vez de embeddings de pago** para la recuperación: funciona sin API
  key ni costo, ideal para desarrollar y probar antes de conectar un LLM real.
  Es intercambiable por un vector store (FAISS/Chroma) con embeddings si el
  volumen de documentos crece.
- **Agente agnóstico de proveedor**: soporta Claude, ChatGPT, Gemini o Cohere
  con solo cambiar una variable de entorno (`LLM_BACKEND`), más un modo `mock`
  para probar el pipeline sin ninguna key.
- **El prompt fuerza al LLM a responder solo con el contexto recuperado** y a
  citar la página, para minimizar respuestas inventadas en un dominio sensible
  como el de salud.

## Ejemplos de preguntas y respuestas

| Pregunta | El agente responde en base a... |
|---|---|
| "¿Qué cobertura tiene MedFuturo?" | La tabla de convenios (pág. 5): 80% de cobertura, requiere autorización previa solo en alta complejidad. |
| "¿Cuánto tiempo debo esperar tras un estudio con sedación antes de manejar?" | Sección 5.5 (pág. 6): 12 horas, y debe retirarse acompañado. |
| "¿Qué pasa si falto a un turno sin avisar?" | Sección 3.2 (pág. 4): la primera inasistencia no tiene cargo; desde la segunda, 50% del valor de la consulta. |
| "¿Con cuánto tiempo puedo cancelar un turno?" | Sección 3.1 (pág. 4): al menos 24 horas de anticipación. |
| "¿Cómo pido una copia de mi historia clínica?" | Sección 1.4 (pág. 2): por correo a privacidad@clinicavitalis.com, respuesta en máx. 10 días hábiles. |

## Estructura del repositorio

```
├── docs/
│   ├── generar_pdf.py              # genera el PDF de políticas (reportlab)
│   └── politicas_clinica_vitalis.pdf
├── src/
│   ├── ingest.py                   # Etapa 1: lee y trocea el PDF
│   ├── retriever.py                # Etapa 2: búsqueda TF-IDF sobre los chunks
│   ├── agente.py                   # Etapa 2: agente RAG (multi-proveedor de LLM)
│   └── api.py                      # Etapa 3: servicio web FastAPI
├── static/
│   └── index.html                  # interfaz de chat
├── data/
│   └── chunks.json                 # generado por ingest.py
├── Dockerfile
├── DEPLOY_OCI.md                    # guía paso a paso del deploy en OCI Compute
├── requirements.txt
├── .env.example
└── README.md
```

## Cómo correrlo localmente

```bash
git clone https://github.com/<tu-usuario>/agente-clinica-vitalis.git
cd agente-clinica-vitalis
python -m venv .venv && source .venv/bin/activate   # opcional pero recomendado
pip install -r requirements.txt

# 1) Generar (o regenerar) los chunks a partir del PDF
python src/ingest.py --pdf docs/politicas_clinica_vitalis.pdf --salida data/chunks.json

# 2) Probar el agente por consola, sin necesidad de ninguna API key
python src/agente.py --interactivo --backend mock

# 3) Levantar el servicio web
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
# abrir http://localhost:8000
```

### Para usar un LLM real (opcional)

```bash
cp .env.example .env
# completar en .env: LLM_BACKEND=anthropic y ANTHROPIC_API_KEY=sk-ant-...
python src/agente.py --interactivo --backend anthropic
```

Backends soportados: `anthropic`, `openai`, `gemini`, `cohere`, `mock`.

## Deploy en OCI

Ver la guía completa en [`DEPLOY_OCI.md`](./DEPLOY_OCI.md): creación de la
instancia (capa Always Free), apertura de puertos, Docker, y verificación
del servicio público.

## Personalización

Este proyecto está pensado para adaptarse a cualquier documento propio:
reemplazá `docs/politicas_clinica_vitalis.pdf` por tu propio PDF (o adaptá
`ingest.py` para leer un CSV con `pandas`) y volvé a correr el pipeline.
