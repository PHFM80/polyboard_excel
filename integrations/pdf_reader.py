# integrations/pdf_reader.py
"""Lectura de PDF generado por Polyboard."""

from __future__ import annotations

from pathlib import Path

import pdfplumber


def read_pages(pdf_path: str) -> list[str]:
    """
    Extrae el texto de cada página del PDF.

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        Lista de cadenas, una por página.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo no es un PDF válido o no se puede leer.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"El archivo no existe: {pdf_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("El archivo no tiene extensión .pdf")

    pages_text: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            pages_text.append(text or "")

    return pages_text
