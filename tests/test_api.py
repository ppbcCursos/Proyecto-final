from datetime import date

from fastapi.testclient import TestClient
import pytest

from folio.api import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "test.sqlite3", clock=lambda: date(2026, 10, 16))) as session:
        yield session


def ask(client, message, **scope):
    response = client.post("/api/chat", json={"message": message, **scope})
    assert response.status_code == 200
    return response.json()


def test_counts_and_citations_share_the_same_catalog(client):
    month = ask(client, "¿Qué libros se publicaron en septiembre de 2026?")
    assert len(month["books"]) == len(month["citations"]) == 6
    for book, citation in zip(month["books"], month["citations"]):
        assert book["id"] == citation["record_id"]
        assert book["title"] in citation["fragment"]
    authors = ask(client, "¿Qué autores han publicado este año y qué libros?")
    assert len(authors["groups"]) == 6
    assert all(g["count"] == len(g["books"]) == 2 for g in authors["groups"])
    assert len(authors["citations"]) == 12
    publishers = ask(client, "¿Qué editoriales han publicado y cuántos libros?")
    assert sorted(g["count"] for g in publishers["groups"]) == [2, 2, 4, 4]


@pytest.mark.parametrize("question", [
    "Libros de noviembre de 2026", "Autores de 2027", "Editoriales de diciembre",
    "Autores el año que viene", "Editoriales el mes que viene", "Libros de mañana",
    "Libros del 20 de octubre de 2026", "Libros del 20/10/2026",
    "Libros del 2026-10-20", "Autores dentro de dos meses", "La próxima semana",
    "¿Qué autores publicarán este año?",
])
def test_future_queries_never_return_titles_or_counts(client, question):
    result = ask(client, question)
    assert result["title"] == "No consta en los datos."
    assert result["reason"] == "future"
    assert result["books"] == result["groups"] == result["citations"] == []


def test_partial_month_excludes_future_releases(client):
    result = ask(client, "Libros de octubre de 2026")
    assert len(result["books"]) == 1
    assert "hasta el día 16" in result["text"]
    assert result["books"][0]["publication_date"] == "2026-10-08"


def test_missing_data_is_not_a_claim_about_market(client):
    result = ask(client, "Libros de abril de 2026")
    assert result["reason"] == "empty"
    assert "no significa" in result["text"]
    assert not result["citations"]


def test_document_filters_apply_to_the_same_entry(client):
    response = client.get("/api/catalog", params={"kind": "document", "search": "REG-001", "month": "2026-09"})
    assert response.json()["total"] == 0
    response = client.get("/api/catalog", params={"kind": "document", "search": "REG-001", "month": "2026-01"})
    assert response.json()["total"] == 1


def test_search_is_accent_insensitive_and_combines_filters(client):
    result = client.get("/api/catalog", params={"search": "Lucia", "month": "2026-09"}).json()
    assert result["total"] == 1
    assert result["items"][0]["id"] == "REG-008"


def test_api_validates_input_and_missing_records(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/chat", json={"message": "Libros", "month": 13}).status_code == 422
    assert client.get("/api/books/REG-999").status_code == 404
    assert client.get("/api/catalog", params={"month": "2026-25"}).status_code == 422
    assert client.get("/api/nonexistent").status_code == 404


def test_demo_sources_are_explicit_and_exported(client):
    source = client.get("/api/sources").json()
    assert len(source["items"]) == 4
    assert "No respaldan" in source["note"]
    assert "ficticios" in client.get("/api/export.csv").text
    assert client.get("/api/health").json()["as_of"] == "2026-10-16"


def test_preference_and_exact_day(client):
    result = ask(client, "No me preguntes por fechas futuras a la del día de la consulta.")
    assert result["kind"] == "preference"
    result = ask(client, "Libros del 3 de septiembre de 2026")
    assert len(result["books"]) == 1
    assert result["books"][0]["id"] == "REG-006"


def test_database_seed_is_idempotent(tmp_path):
    path = tmp_path / "repeat.sqlite3"
    for _ in range(2):
        with TestClient(create_app(path, clock=lambda: date(2026, 10, 16))) as client:
            assert client.get("/api/catalog").json()["total"] == 12
