# domain/models.py
"""Modelos de dominio del módulo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessResult:
    """Resultado del procesamiento PDF → Excel."""

    ok: bool
    file_path: str | None
    errors: list[str]


@dataclass(frozen=True)
class CorteRow:
    """Una fila de la Lista de Corte (Dimensiones Netas) del PDF."""

    material: str
    referencia: str
    mueble: str
    altura_mm: float
    anchura_mm: float
    cantidad: int
    canto_izq: str
    canto_der: str
    canto_inf: str
    canto_sup: str


@dataclass
class ExtractedData:
    """Datos extraídos del PDF listos para transformar al formato proveedor."""

    lista_corte: list[CorteRow]
    espesor_por_material: dict[str, str]
