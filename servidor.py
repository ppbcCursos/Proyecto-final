"""Servidor RAG de Folio. Arranque: uv run servidor.py (puerto 8000)."""

import argparse
import asyncio
import logging

import uvicorn

from folio.api import create_app

app = create_app(prepare_rag_on_startup=True)


async def preparar_indice():
    async with app.router.lifespan_context(app):
        service = app.state.get_rag_service()
        print(f"Índice preparado: {len(service.records)} registros, {service.index_path.relative_to(service.root)}")
        print("Embeddings reutilizados del disco." if service.loaded_from_disk else "Embeddings creados y guardados en disco.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preparar-indice", action="store_true", help="Generar los documentos y preparar o verificar el índice sin iniciar HTTP.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if args.preparar_indice:
        asyncio.run(preparar_indice())
    else:
        uvicorn.run(app, host="127.0.0.1", port=8000)
