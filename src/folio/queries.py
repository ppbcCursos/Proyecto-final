"""Consultas guiadas: solo se responde con registros persistidos y sus evidencias.

No utiliza un modelo generativo ni completa libros, autores o cantidades ausentes.
"""

from datetime import date, timedelta
import re

from pydantic import BaseModel, Field

from .catalog import citations, groups, normalize

MONTHS = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    year: int | None = Field(default=None, ge=1, le=9999)
    month: int | None = Field(default=None, ge=1, le=12)


def answer(request: ChatRequest, records: list[dict], as_of: date) -> dict:
    q = normalize(request.message)
    result = {
        "question": request.message,
        "kind": "help",
        "title": "Pregunta al catálogo",
        "text": "Puedes consultar libros de un mes, autores y sus libros, o editoriales y sus recuentos.",
        "note": "Consultas guiadas sobre el catálogo ficticio; sin llamadas externas.",
        "as_of": as_of.isoformat(),
        "books": [], "groups": [], "citations": [], "reason": None,
    }

    def no_data(reason: str, note: str) -> dict:
        return {**result, "kind": "no_data", "title": "No consta en los datos.", "text": note, "note": "No se han inventado registros ni recuentos. Un anuncio no acredita una publicación.", "reason": reason}

    if re.search(r"\bno (?:me )?(?:preguntes|propongas|sugieras)\b", q) and re.search(r"futur|fecha|proxim", q):
        return {**result, "kind": "preference", "title": "Preferencia aplicada", "text": f"Usaré como límite el {as_of:%d/%m/%Y}. No propondré fechas posteriores y, si preguntas por ellas, indicaré que no constan en los datos.", "note": "La fecha de consulta se calcula en la zona horaria Europe/Madrid."}

    years = [int(y) for y in re.findall(r"\b(\d{4})\b", q)]
    year = max(years) if years else request.year or as_of.year
    month_names = [i + 1 for i, month in enumerate(MONTHS) if re.search(rf"\b{month}\b", q)]
    if re.search(r"\bsetiembre\b", q):
        month_names.append(9)
    month = month_names[0] if len(month_names) == 1 else request.month
    exact: date | None = None
    numeric = re.search(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b", q)
    iso = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", q)
    natural_day = re.search(r"\b(\d{1,2})\s+(?:de\s+)?(" + "|".join(MONTHS) + r")\b", q)
    try:
        if numeric:
            exact = date(int(numeric[3]), int(numeric[2]), int(numeric[1]))
        elif iso:
            exact = date.fromisoformat(iso[0])
        elif natural_day:
            exact = date(year, MONTHS.index(natural_day[2]) + 1, int(natural_day[1]))
        elif re.search(r"\b(?:hoy|ayer|anteayer)\b", q):
            exact = as_of - timedelta(days=2 if "anteayer" in q else 1 if "ayer" in q else 0)
        if exact:
            year, month = exact.year, exact.month
    except ValueError:
        return {**result, "text": "La fecha no es válida. Indica un mes y un año, por ejemplo: septiembre de 2026."}

    relative_future = re.search(r"\b(?:manana|pasado manana|proxim[oa]s?|futur[oa]s?|ano que viene|mes que viene|semana que viene|dentro de|el ano siguiente|el mes siguiente|publicaran|saldran|publicara)\b", q)
    if relative_future or year > as_of.year or exact and exact > as_of or month and date(year, month, 1) > as_of:
        return no_data("future", f"La fecha de consulta es el {as_of:%d/%m/%Y}. El periodo solicitado es posterior; no puedo confirmar libros, autores ni cantidades para esa fecha.")
    if len(month_names) > 1 or len(set(years)) > 1:
        return {**result, "text": "Esta aplicación consulta un mes o un año cada vez. Indica un único periodo."}
    if "ano pasado" in q:
        year = as_of.year - 1
    if "mes pasado" in q:
        previous = as_of.replace(day=1) - timedelta(days=1)
        year, month = previous.year, previous.month
    elif "este mes" in q:
        year, month = as_of.year, as_of.month

    selected = [b for b in records if int(b["publication_date"][:4]) == year]
    if month:
        selected = [b for b in selected if int(b["publication_date"][5:7]) == month]
    if exact:
        selected = [b for b in selected if b["publication_date"] == exact.isoformat()]

    named_author = next((b["author"] for b in records if normalize(b["author"]) in q), None)
    named_publisher = next((b["publisher"] for b in records if normalize(b["publisher"]) in q), None)
    if named_author:
        selected = [b for b in selected if b["author"] == named_author]
    if named_publisher:
        selected = [b for b in selected if b["publisher"] == named_publisher]

    kind = "publishers" if "editorial" in q and not named_publisher else "authors" if re.search(r"\b(?:autores|autoras|autorias|escritores|escritoras)\b", q) and not named_author else "books" if month or exact or named_author or named_publisher or re.search(r"\b(?:libros|titulos|publicaciones|novedades)\b", q) else None
    if kind is None:
        return result
    if not selected:
        return no_data("empty", f"No hay registros coincidentes para el periodo solicitado, hasta el {as_of:%d/%m/%Y}. Esto no significa que no se publicaran libros en el mercado.")

    period = f"{MONTHS[month - 1]} de {year}" if month else str(year)
    if exact:
        period = f"{exact:%d/%m/%Y}"
    partial = year == as_of.year and month == as_of.month and exact is None
    period += f", hasta el día {as_of.day}" if partial else ""
    group_data = groups(selected, "author" if kind == "authors" else "publisher") if kind != "books" else []
    count = len(selected)
    titles = {"books": "Libros publicados", "authors": "Las voces del catálogo", "publishers": "El mapa de las editoriales"}
    text = f"En {period} constan {count} {'libro' if count == 1 else 'libros'} en castellano en este catálogo."
    if kind == "authors":
        text = f"En {period}, {len(group_data)} autores y autoras tienen {count} libros registrados."
    elif kind == "publishers":
        text = f"En {period}, {len(group_data)} editoriales suman {count} libros registrados."
    return {**result, "kind": kind, "title": titles[kind], "text": text, "note": f"Catálogo ficticio y no exhaustivo. Publicaciones hasta el {as_of:%d/%m/%Y}; un registro único por libro.", "books": selected if kind == "books" else [], "groups": group_data, "citations": citations(selected)}
