"""Contrato JSON del RAG y esquema estructurado que recibe el modelo."""

from datetime import date
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class Mensaje(BaseModel):
    role: Literal["user", "assistant"] = Field(validation_alias=AliasChoices("role", "rol"))
    content: str = Field(max_length=4000, validation_alias=AliasChoices("content", "contenido"))

    @field_validator("role", mode="before")
    @classmethod
    def traducir_rol(cls, value):
        return {"usuario": "user", "asistente": "assistant"}.get(value, value)


class Pregunta(BaseModel):
    pregunta: str = Field(min_length=1, max_length=2000)
    historial: list[Mensaje] = Field(default_factory=list, max_length=20)

    @field_validator("pregunta")
    @classmethod
    def no_vacia(cls, value):
        if not value.strip():
            raise ValueError("La pregunta no puede estar vacía.")
        return value.strip()


class DecisionModelo(BaseModel):
    """El modelo selecciona hechos; no puede crear títulos, fechas ni cantidades."""

    model_config = ConfigDict(extra="forbid")
    consta: bool
    tipo: Literal["libros", "autores", "editoriales", "detalle"]
    registros: list[str]


class Libro(BaseModel):
    registro_id: str
    titulo: str
    autor: str
    editorial: str
    fecha_publicacion: date
    idioma: str
    genero: str


class Fuente(BaseModel):
    documento_id: str
    documento: str
    registro_id: str
    fragmento: str
    similitud: float = Field(ge=-1, le=1)
    datos_ficticios: bool


class Grupo(BaseModel):
    nombre: str
    cantidad: int
    libros: list[Libro]


class Respuesta(BaseModel):
    pregunta: str
    pregunta_contextualizada: str
    respuesta: str
    estado: Literal["respondido", "no_consta", "preferencia"]
    motivo: str | None = None
    fecha_consulta: date
    modelo_usado: bool
    fuentes: list[Fuente] = Field(default_factory=list)
    libros: list[Libro] = Field(default_factory=list)
    autores: list[Grupo] = Field(default_factory=list)
    editoriales: list[Grupo] = Field(default_factory=list)
    aviso: str = "Catálogo ficticio de demostración; no representa todo el mercado editorial."


class Documento(BaseModel):
    id: str
    titulo: str
    editorial: str
    archivo: str
    cantidad_registros: int
    registros: list[Libro]
    fragmentos: list[Fuente]
    datos_ficticios: bool = True


class ListadoDocumentos(BaseModel):
    documentos: list[Documento]
    registros: list[Libro]
    total_documentos: int
    total_registros: int
    fecha_consulta: date
    aviso: str = "Documentos locales generados con los datos ficticios de maquetas.html."


def libro(record: dict) -> Libro:
    return Libro(
        registro_id=record["id"], titulo=record["title"], autor=record["author"],
        editorial=record["publisher"], fecha_publicacion=record["publication_date"],
        idioma=record["language"], genero=record["genre"],
    )
