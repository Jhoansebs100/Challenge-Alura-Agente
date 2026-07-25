# -*- coding: utf-8 -*-
"""
agente.py
---------
Etapa 2 del proyecto: el agente de IA que responde preguntas sobre el
documento, usando el patrón RAG (Retrieval-Augmented Generation):

    pregunta -> Retriever (retriever.py) busca los chunks más relevantes
             -> se arma un prompt con esos chunks como contexto
             -> un LLM redacta la respuesta final en lenguaje natural

El agente es agnóstico del proveedor de LLM: soporta Anthropic (Claude),
OpenAI (ChatGPT), Google (Gemini) y Cohere, seleccionables por parámetro
o variable de entorno. También incluye un backend "mock" que no requiere
ninguna API key, pensado para probar el pipeline de recuperación sin
gastar créditos ni depender de internet.

Configuración (crear un archivo .env a partir de .env.example):
    LLM_BACKEND=anthropic        # anthropic | openai | gemini | cohere | mock
    ANTHROPIC_API_KEY=...
    OPENAI_API_KEY=...
    GOOGLE_API_KEY=...
    COHERE_API_KEY=...

Uso:
    python src/agente.py --pregunta "¿Qué cobertura tiene MedFuturo?"
    python src/agente.py --interactivo
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from retriever import Retriever

load_dotenv()

PROMPT_SISTEMA = (
    "Sos un asistente virtual de la Clínica Vitalis. Respondé la pregunta del "
    "paciente de forma clara, breve y en español, usando EXCLUSIVAMENTE la "
    "información del CONTEXTO provisto. Si el contexto no alcanza para "
    "responder, decilo explícitamente en vez de inventar datos. Cuando sea "
    "útil, mencioná el número de página de la que sale la información."
)


def armar_prompt(pregunta: str, chunks: list[dict]) -> str:
    contexto = "\n\n".join(
        f"[Página {c['pagina']}] {c['texto']}" for c in chunks
    )
    return (
        f"CONTEXTO:\n{contexto}\n\n"
        f"PREGUNTA DEL PACIENTE:\n{pregunta}\n\n"
        f"RESPUESTA:"
    )


# ---------------------------------------------------------------------------
# Backends de LLM. Cada función recibe (prompt, modelo) y devuelve un string.
# ---------------------------------------------------------------------------

def _backend_anthropic(prompt: str, modelo: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model=modelo or "claude-sonnet-4-6",
        max_tokens=500,
        system=PROMPT_SISTEMA,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def _backend_openai(prompt: str, modelo: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=modelo or "gpt-4o-mini",
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
    )
    return resp.choices[0].message.content


def _backend_gemini(prompt: str, modelo: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel(
        modelo or "gemini-1.5-flash",
        system_instruction=PROMPT_SISTEMA,
    )
    resp = model.generate_content(prompt)
    return resp.text


def _backend_cohere(prompt: str, modelo: str) -> str:
    import cohere
    client = cohere.Client(os.environ["COHERE_API_KEY"])
    resp = client.chat(
        model=modelo or "command-r",
        preamble=PROMPT_SISTEMA,
        message=prompt,
    )
    return resp.text


def _backend_mock(prompt: str, modelo: str) -> str:
    """
    Backend sin API key: no "redacta" con un LLM real, sólo devuelve el
    contexto recuperado de forma legible. Sirve para verificar que el
    Retriever encuentra la información correcta antes de conectar un LLM.
    """
    return (
        "[MODO MOCK — sin LLM conectado]\n"
        "No hay una API key configurada, así que te muestro el fragmento del "
        "documento que el buscador considera más relevante para tu pregunta:\n\n"
        + prompt.split("PREGUNTA DEL PACIENTE:")[0].replace("CONTEXTO:\n", "")
    )


BACKENDS = {
    "anthropic": _backend_anthropic,
    "openai": _backend_openai,
    "gemini": _backend_gemini,
    "cohere": _backend_cohere,
    "mock": _backend_mock,
}


class AgenteClinica:
    def __init__(self, ruta_chunks: str = "data/chunks.json",
                 backend: str | None = None, modelo: str | None = None, k: int = 3):
        self.retriever = Retriever(ruta_chunks)
        self.backend = backend or os.environ.get("LLM_BACKEND", "mock")
        self.modelo = modelo or os.environ.get("LLM_MODEL")
        self.k = k

        if self.backend not in BACKENDS:
            raise ValueError(
                f"Backend '{self.backend}' no soportado. Opciones: {list(BACKENDS)}"
            )

    def responder(self, pregunta: str) -> dict:
        chunks = self.retriever.buscar(pregunta, k=self.k)

        if not chunks:
            return {
                "respuesta": "No encontré información relacionada en el manual de políticas.",
                "fuentes": [],
            }

        prompt = armar_prompt(pregunta, chunks)
        funcion_backend = BACKENDS[self.backend]
        respuesta = funcion_backend(prompt, self.modelo)

        return {
            "respuesta": respuesta,
            "fuentes": [{"pagina": c["pagina"], "score": round(c["score"], 3)} for c in chunks],
        }


def main():
    parser = argparse.ArgumentParser(description="Agente de preguntas y respuestas de la Clínica Vitalis.")
    parser.add_argument("--pregunta", help="Pregunta puntual (modo no interactivo).")
    parser.add_argument("--interactivo", action="store_true", help="Inicia un chat en la terminal.")
    parser.add_argument("--backend", choices=list(BACKENDS), default=None,
                         help="Proveedor de LLM (por defecto: variable LLM_BACKEND o 'mock').")
    parser.add_argument("--modelo", default=None, help="Nombre del modelo específico a usar.")
    parser.add_argument("--chunks", default="data/chunks.json")
    parser.add_argument("--k", type=int, default=3, help="Cantidad de fragmentos a recuperar.")
    args = parser.parse_args()

    agente = AgenteClinica(args.chunks, backend=args.backend, modelo=args.modelo, k=args.k)
    print(f"(backend activo: {agente.backend})\n")

    if args.interactivo:
        print("Agente de la Clínica Vitalis — escribí 'salir' para terminar.\n")
        while True:
            pregunta = input("Vos: ").strip()
            if pregunta.lower() in {"salir", "exit", "quit"}:
                break
            if not pregunta:
                continue
            resultado = agente.responder(pregunta)
            print(f"\nAgente: {resultado['respuesta']}")
            print(f"(fuentes: {resultado['fuentes']})\n")
    elif args.pregunta:
        resultado = agente.responder(args.pregunta)
        print(f"Pregunta: {args.pregunta}\n")
        print(f"Respuesta: {resultado['respuesta']}\n")
        print(f"Fuentes: {resultado['fuentes']}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
