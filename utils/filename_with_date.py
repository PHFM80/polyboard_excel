# utils/filename_with_date.py
"""Añade la fecha al nombre del archivo antes de la extensión."""

from __future__ import annotations

from datetime import date
from pathlib import Path


def add_date_to_filename(file_path: str, fecha: date | None = None) -> str:
    """
    Inserta la fecha en el nombre del archivo: 'carpeta/archivo.xlsx' -> 'carpeta/archivo_2025-02-13.xlsx'.

    Args:
        file_path: Ruta del archivo.
        fecha: Fecha a usar; si es None, se usa hoy.
    """
    if fecha is None:
        fecha = date.today()
    path = Path(file_path)
    stem = path.stem
    suffix = path.suffix
    new_name = f"{stem}_{fecha:%Y-%m-%d}{suffix}"
    return str(path.parent / new_name)
