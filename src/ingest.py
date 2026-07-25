# -*- coding: utf-8 -*-
"""
ingest.py
---------
Etapa 1 del proyecto: lectura y procesamiento del documento.

Este script:
1. Lee el PDF con las políticas de la Clínica Vitalis (pypdf).
2. Extrae el texto de cada página.
3. Limpia el texto (espacios, saltos de línea sueltos).
4. Divide el contenido en "chunks" (fragmentos) con solapamiento,
   usando el splitter de LangChain, para que luego puedan convertirse
   en embeddings y usarse en el agente de preguntas y respuestas (Etapa 2).
5. Guarda los chunks en un archivo JSON intermedio (data/chunks.json)
   para inspeccionarlos o reutilizarlos sin tener que releer el PDF.

Uso:
    python src/ingest.py --pdf docs/politicas_clinica_vitalis.pdf
"""

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader
try:
    # LangChain >= 0.2 movió los text splitters a su propio paquete
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter


def leer_pdf(ruta_pdf: str) -> list[dict]:
    """Lee el PDF y devuelve una lista de dicts {pagina, texto}."""
    reader = PdfReader(ruta_pdf)
    paginas = []
    for i, page in enumerate(reader.pages, start=1):
        texto = page.extract_text() or ""
        paginas.append({"pagina": i, "texto": texto})
    return paginas


def limpiar_texto(texto: str) -> str:
    """Normaliza espacios y saltos de línea del texto extraído."""
    texto = re.sub(r"\n{2,}", "\n", texto)
    texto = re.sub(r"[ \t]{2,}", " ", texto)
    return texto.strip()


def dividir_en_chunks(paginas: list[dict], chunk_size: int = 800,
                       chunk_overlap: int = 120) -> list[dict]:
    """
    Divide el texto de cada página en fragmentos más pequeños (chunks),
    conservando de qué página proviene cada uno (útil para citar la fuente
    en las respuestas del agente).
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for pagina in paginas:
        texto = limpiar_texto(pagina["texto"])
        if not texto:
            continue
        fragmentos = splitter.split_text(texto)
        for j, fragmento in enumerate(fragmentos):
            chunks.append({
                "id": f"p{pagina['pagina']}_c{j}",
                "pagina": pagina["pagina"],
                "texto": fragmento,
            })
    return chunks


def guardar_chunks(chunks: list[dict], ruta_salida: str) -> None:
    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Ingesta y chunking del PDF de la clínica.")
    parser.add_argument("--pdf", default="docs/politicas_clinica_vitalis.pdf",
                         help="Ruta al archivo PDF de entrada.")
    parser.add_argument("--salida", default="data/chunks.json",
                         help="Ruta del JSON de salida con los chunks.")
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--chunk-overlap", type=int, default=120)
    args = parser.parse_args()

    print(f"Leyendo PDF: {args.pdf}")
    paginas = leer_pdf(args.pdf)
    print(f"  -> {len(paginas)} páginas extraídas.")

    print("Dividiendo en chunks...")
    chunks = dividir_en_chunks(paginas, args.chunk_size, args.chunk_overlap)
    print(f"  -> {len(chunks)} chunks generados.")

    guardar_chunks(chunks, args.salida)
    print(f"Chunks guardados en: {args.salida}")

    # Muestra un ejemplo para verificar visualmente el resultado
    if chunks:
        print("\nEjemplo de chunk:")
        print(json.dumps(chunks[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
