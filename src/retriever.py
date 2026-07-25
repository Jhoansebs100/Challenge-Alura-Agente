# -*- coding: utf-8 -*-
"""
retriever.py
------------
Motor de búsqueda semántica simple sobre los chunks generados por ingest.py.

Usamos TF-IDF + similitud coseno (scikit-learn) en lugar de embeddings de un
LLM externo por dos motivos:
  1. Funciona 100% offline, sin API key ni costo, ideal para desarrollar y
     probar el pipeline antes de conectar un modelo de lenguaje real.
  2. Es fácilmente reemplazable: si más adelante querés usar embeddings de
     OpenAI, Cohere o un modelo local (sentence-transformers), solo hace
     falta cambiar la clase `Retriever` por otra con la misma interfaz
     (`buscar(pregunta, k)` -> lista de chunks).

Para producción con más volumen de documentos, se recomienda migrar a un
vector store (FAISS, Chroma, pgvector) con embeddings reales.
"""

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Retriever:
    def __init__(self, ruta_chunks: str = "data/chunks.json"):
        self.chunks = self._cargar_chunks(ruta_chunks)
        textos = [c["texto"] for c in self.chunks]

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
        )
        self.matriz = self.vectorizer.fit_transform(textos)

    @staticmethod
    def _cargar_chunks(ruta_chunks: str) -> list[dict]:
        ruta = Path(ruta_chunks)
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encontró '{ruta_chunks}'. Corré primero: python src/ingest.py"
            )
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    def buscar(self, pregunta: str, k: int = 3) -> list[dict]:
        """Devuelve los k chunks más relevantes para la pregunta, con su score."""
        vector_pregunta = self.vectorizer.transform([pregunta])
        similitudes = cosine_similarity(vector_pregunta, self.matriz)[0]

        indices_ordenados = similitudes.argsort()[::-1][:k]
        resultados = []
        for idx in indices_ordenados:
            if similitudes[idx] <= 0:
                continue
            chunk = dict(self.chunks[idx])
            chunk["score"] = float(similitudes[idx])
            resultados.append(chunk)
        return resultados


if __name__ == "__main__":
    # Prueba rápida desde la línea de comandos
    r = Retriever("data/chunks.json")
    pregunta = "¿Cuánto tiempo debo esperar tras un estudio con sedación?"
    for chunk in r.buscar(pregunta, k=3):
        print(f"[pág. {chunk['pagina']} | score={chunk['score']:.3f}] {chunk['texto'][:120]}...")
