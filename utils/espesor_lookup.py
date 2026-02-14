# utils/espesor_lookup.py
"""Resuelve espesor para un material que puede estar truncado en el PDF."""

from __future__ import annotations


def buscar_espesor(material: str, espesor_por_material: dict[str, str]) -> str:
    """
    Devuelve el espesor (str) para un material.
    Si el material viene truncado (ej. "gris sombr..."), busca una clave que coincida.
    """
    if not material:
        return ""
    material_limpio = material.split("...")[0].strip().lower()
    for clave, espesor in espesor_por_material.items():
        if clave.lower().startswith(material_limpio) or material_limpio.startswith(clave.lower().split(",")[0]):
            return espesor
    return ""
