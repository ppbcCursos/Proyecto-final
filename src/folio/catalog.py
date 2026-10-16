"""Persistencia local y selección de las evidencias de cada respuesta."""

from collections import defaultdict
from contextlib import contextmanager
from datetime import date
from pathlib import Path
import sqlite3
import unicodedata

from .sample_data import PUBLISHERS, SAMPLE_BOOKS


def normalize(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", value.casefold()) if not unicodedata.combining(c))


@contextmanager
def connection(path: Path):
    database = sqlite3.connect(path, timeout=15)
    database.row_factory = sqlite3.Row
    try:
        yield database
        database.commit()
    except Exception:
        database.rollback()
        raise
    finally:
        database.close()


def initialize(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with connection(path) as database:
        database.execute("""CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY, publication_date TEXT NOT NULL,
            title TEXT NOT NULL, author TEXT NOT NULL, publisher TEXT NOT NULL,
            genre TEXT NOT NULL, cover_color TEXT NOT NULL,
            document_id TEXT NOT NULL, language TEXT NOT NULL,
            fragment TEXT NOT NULL, is_demo INTEGER NOT NULL DEFAULT 1
        )""")
        for record in SAMPLE_BOOKS:
            record_id, published, title, author, publisher, genre, color = record
            fragment = (
                f"Título: {title}. Autoría: {author}. Editorial: {publisher}. "
                f"Fecha de publicación: {date.fromisoformat(published):%d/%m/%Y}. "
                f"Idioma de la edición: castellano. Género: {genre}."
            )
            database.execute(
                "INSERT OR IGNORE INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*record, f"DOC-{PUBLISHERS.index(publisher) + 1:03}", "Castellano", fragment, 1),
            )


def books(path: Path, as_of: date) -> list[dict]:
    with connection(path) as database:
        records = database.execute(
            "SELECT * FROM books WHERE publication_date <= ? ORDER BY publication_date, id",
            (as_of.isoformat(),),
        ).fetchall()
    return [{**dict(record), "is_demo": bool(record["is_demo"])} for record in records]


def matches(record: dict, search: str) -> bool:
    return not search or normalize(search) in normalize(" ".join(str(record.get(key, "")) for key in ("id", "title", "author", "publisher")))


def documents(records: list[dict]) -> list[dict]:
    grouped: dict[str, list] = defaultdict(list)
    for record in records:
        grouped[record["document_id"]].append(record)
    return [
        {
            "id": key,
            "title": f"Catálogo 2026 · {items[0]['publisher']}",
            "publisher": items[0]["publisher"],
            "is_demo": True,
            "records": items,
            "record_count": len(items),
            "type": "document",
        }
        for key, items in sorted(grouped.items())
    ]


def groups(records: list[dict], field: str) -> list[dict]:
    grouped: dict[str, list] = defaultdict(list)
    for record in records:
        grouped[record[field]].append(record)
    return [
        {"label": key, "count": len(items), "books": items}
        for key, items in sorted(grouped.items(), key=lambda item: (-len(item[1]), normalize(item[0])))
    ]


def citations(records: list[dict]) -> list[dict]:
    return [
        {"record_id": b["id"], "document_id": b["document_id"], "label": f"{b['id']} · Ficha editorial", "fragment": b["fragment"], "is_demo": b["is_demo"]}
        for b in records
    ]
