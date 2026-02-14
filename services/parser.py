# services/parser.py
"""Orquestador de parseo: une texto de páginas y delega en parsers específicos."""

from __future__ import annotations

from ..domain.models import ExtractedData
from .parsers.lista_corte import parse_lista_corte
from .parsers.resumen import parse_espesor_por_material


def parse_pages(pages_text: list[str]) -> ExtractedData:
    """
    Convierte el texto de todas las páginas en ExtractedData (lista de corte + espesores).
    """
    texto_completo = "\n".join(pages_text or [])
    lista_corte = parse_lista_corte(texto_completo)
    espesor_por_material = parse_espesor_por_material(texto_completo)
    return ExtractedData(
        lista_corte=lista_corte,
        espesor_por_material=espesor_por_material,
    )
