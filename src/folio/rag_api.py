"""Rutas del RAG: creadas antes de la ruta de la interfaz, con servicio inyectable."""

import threading

from fastapi import FastAPI, HTTPException, Query

from .rag import RagError, RagService
from .rag_models import ListadoDocumentos, Pregunta, Respuesta


def install_rag(application: FastAPI, database_path, root, clock, factory=None):
    lock = threading.Lock()
    application.state.rag_service = None

    def service():
        if application.state.rag_service is None:
            with lock:
                if application.state.rag_service is None:
                    application.state.rag_service = factory(database_path, root, clock) if factory else RagService(database_path, root, clock)
        return application.state.rag_service

    application.state.get_rag_service = service

    @application.post("/api/preguntar", response_model=Respuesta)
    def preguntar(request: Pregunta):
        try:
            return service().ask(request)
        except RagError as error:
            raise HTTPException(503, str(error)) from None

    @application.get("/api/documentos", response_model=ListadoDocumentos)
    def documentos(
        buscar: str = Query(default="", max_length=200),
        mes: str = Query(default="", pattern=r"^(?:\d{4}-(?:0[1-9]|1[0-2]))?$"),
        editorial: str = Query(default="", max_length=200),
    ):
        return service().list_documents(buscar, mes, editorial)
