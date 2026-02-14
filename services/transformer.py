# services/transformer.py
"""Transformación de datos extraídos al formato columnas del proveedor."""

from __future__ import annotations

from ..domain.models import ExtractedData
from ..utils.espesor_lookup import buscar_espesor
from .veta import inferir_veta

# Columnas exigidas por el instructivo del proveedor (planilla multipedido)
COLUMNAS_PROVEEDOR = (
    "DESCRIPCION",
    "COLOR",
    "ESPESOR",
    "LONGITUD",
    "ANCHO",
    "CANTIDAD",
    "VETA",
    "CANTEADO",
    "PEGADO PVC",
)


def to_provider_rows(extracted: ExtractedData) -> list[dict[str, str | int]]:
    """
    Convierte ExtractedData en filas para Excel del proveedor.
    Altura → LONGITUD, Anchura → ANCHO. CANTEADO y PEGADO PVC vacíos por ahora.
    """
    rows: list[dict[str, str | int]] = []
    for row in extracted.lista_corte:
        espesor = buscar_espesor(row.material, extracted.espesor_por_material)
        veta = inferir_veta(row.material)
        descripcion = (row.referencia or "").strip()
        if row.mueble:
            descripcion = f"{descripcion}_{row.mueble}" if descripcion else row.mueble
        rows.append({
            "DESCRIPCION": descripcion,
            "COLOR": row.material or "",
            "ESPESOR": espesor,
            "LONGITUD": int(round(row.altura_mm)),
            "ANCHO": int(round(row.anchura_mm)),
            "CANTIDAD": row.cantidad,
            "VETA": veta,
            "CANTEADO": "",
            "PEGADO PVC": "",
        })
    return rows
