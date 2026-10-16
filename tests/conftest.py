"""Todos los temporales de pruebas permanecen en la carpeta del proyecto."""

from pathlib import Path
from uuid import uuid4


def pytest_configure(config):
    if config.option.basetemp is None:
        root = Path(__file__).resolve().parents[1]
        config.option.basetemp = str(root / ".runtime" / "tests" / uuid4().hex / "tmp")
    Path(config.option.basetemp).parent.mkdir(parents=True, exist_ok=True)
