# services/parsers/resumen.py
"""Extrae material → espesor del bloque Resumen / Panel del PDF."""

from __future__ import annotations

import re


def parse_espesor_por_material(texto_paginas: str) -> dict[str, str]:
    """
    Busca la tabla Panel en Resumen y devuelve mapa material -> espesor (sin unidad).

    Formato esperado: "material, 18.00 1.23 m² ..." → espesor "18".
    """
    out: dict[str, str] = {}
    if "Resumen" not in texto_paginas or "Panel" not in texto_paginas:
        return out

    # Líneas tipo "gris sombra, 18.00 13.45 m²" o "MELA_BL, 18.00 1.53 m²"
    pattern = re.compile(r"^(.+?),?\s+([\d.]+)\s+[\d.]+\s*m²", re.MULTILINE)
    for m in pattern.finditer(texto_paginas):
        material = m.group(1).strip().rstrip(",")
        if material.lower() == "total":
            continue
        espesor = m.group(2)
        if "." in espesor:
            espesor = espesor.rstrip("0").rstrip(".")
        out[material] = espesor
    return out
