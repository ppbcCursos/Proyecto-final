"""API local de Folio. Ejecutar: uv run uvicorn folio.api:app --reload."""

from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Literal
from zoneinfo import ZoneInfo
import csv
import io
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response

from . import catalog
from .queries import ChatRequest, answer
from .sample_data import SOURCES

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env", override=False)


def madrid_today() -> date:
    return datetime.now(ZoneInfo("Europe/Madrid")).date()


def create_app(database_path: Path | None = None, clock: Callable[[], date] = madrid_today) -> FastAPI:
    database_path = database_path or Path(os.getenv("FOLIO_DATABASE", str(ROOT / "data" / "folio.sqlite3")))
    if not database_path.is_absolute():
        database_path = ROOT / database_path

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        catalog.initialize(database_path)
        yield

    application = FastAPI(title="Folio · API editorial", version="0.1.0", lifespan=lifespan)

    def records():
        return catalog.books(database_path, clock())

    @application.get("/api/health")
    def health():
        return {"status": "ok", "as_of": clock(), "timezone": "Europe/Madrid", "mode": "demo"}

    @application.get("/api/catalog")
    def get_catalog(
        search: str = Query(default="", max_length=200),
        month: str = Query(default="", pattern=r"^(?:\d{4}-(?:0[1-9]|1[0-2]))?$"),
        publisher: str = Query(default="", max_length=200),
        kind: Literal["all", "record", "document"] = "record",
    ):
        all_records = records()

        def in_period(record):
            return (not month or record["publication_date"].startswith(month)) and (not publisher or record["publisher"] == publisher)

        filtered = [b for b in all_records if in_period(b) and catalog.matches(b, search)]
        filtered_docs = [
            d for d in catalog.documents(all_records)
            if (not publisher or d["publisher"] == publisher)
            and (
                catalog.matches(d, search) and any(in_period(b) for b in d["records"])
                or any(in_period(b) and catalog.matches(b, search) for b in d["records"])
            )
        ]
        items = ([{**b, "type": "record"} for b in filtered] if kind != "document" else []) + (filtered_docs if kind != "record" else [])
        return {"items": items, "total": len(items), "as_of": clock(), "mode": "demo"}

    @application.get("/api/stats")
    def stats():
        all_records = records()
        current = clock()
        current_records = [b for b in all_records if b["publication_date"].startswith(str(current.year))]
        return {
            "as_of": current, "mode": "demo", "books": len(all_records),
            "authors": len({b["author"] for b in all_records}),
            "publishers": sorted({b["publisher"] for b in all_records}),
            "documents": len(catalog.documents(all_records)),
            "years": sorted({int(b["publication_date"][:4]) for b in all_records} | {current.year}, reverse=True),
            "months": [{"month": i, "count": sum(int(b["publication_date"][5:7]) == i for b in current_records), "state": "future" if i > current.month else "partial" if i == current.month else "past"} for i in range(1, 13)],
        }

    @application.get("/api/books/{record_id}")
    def get_book(record_id: str):
        book = next((b for b in records() if b["id"] == record_id), None)
        if not book:
            raise HTTPException(404, "No consta ese registro en los datos disponibles.")
        return book

    @application.get("/api/documents/{document_id}")
    def get_document(document_id: str):
        document = next((d for d in catalog.documents(records()) if d["id"] == document_id), None)
        if not document:
            raise HTTPException(404, "No consta ese documento en los datos disponibles.")
        return document

    @application.get("/api/sources")
    def sources():
        return {"items": SOURCES, "researched_on": "2026-10-16", "as_of": clock(), "note": "Fuentes reales investigadas. No respaldan los registros ficticios ni se sincronizan automáticamente."}

    @application.post("/api/chat")
    def chat(request: ChatRequest):
        return answer(request, records(), clock())

    @application.get("/api/export.csv")
    def export_catalog():
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["Registro", "Título", "Autoría", "Editorial", "Publicación", "Género", "Idioma", "Fragmento", "Nota"])
        for book in records():
            writer.writerow([book[k] for k in ("id", "title", "author", "publisher", "publication_date", "genre", "language", "fragment")] + ["Datos ficticios de demostración"])
        return Response("\ufeff" + stream.getvalue(), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": 'attachment; filename="folio-catalogo-demo.csv"'})

    @application.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if path == "api" or path.startswith("api/"):
            raise HTTPException(404, "Ruta de API no encontrada.")
        dist = (ROOT / "web" / "dist").resolve()
        target = (dist / path).resolve()
        if not target.is_relative_to(dist):
            raise HTTPException(404)
        if target.is_file():
            return FileResponse(target)
        index = dist / "index.html"
        if index.is_file() and (not path or not Path(path).suffix):
            return FileResponse(index)
        raise HTTPException(503 if not index.exists() else 404, "Interfaz no compilada. Ejecuta npm run build dentro de web/ o usa Vite en el puerto 5173.")

    return application


app = create_app()
