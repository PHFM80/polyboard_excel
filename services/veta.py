# services/veta.py
"""Inferencia de VETA (LONGITUD / NINGUNA) según material."""

from __future__ import annotations

# Materiales que típicamente tienen veta (madera, terciado).
# Melamina/MDF sin veta → NINGUNA.
_MATERIALES_CON_VETA = (
    "terciado",
    "cedro",
    "pino",
    "fibroplus",
)


def inferir_veta(material: str) -> str:
    """
    Devuelve "LONGITUD" si el material tiene veta, "NINGUNA" si no.
    Por ahora se infiere por nombre de material.
    """
    if not (material or "").strip():
        return "NINGUNA"
    low = material.lower()
    for clave in _MATERIALES_CON_VETA:
        if clave in low:
            return "LONGITUD"
    return "NINGUNA"
