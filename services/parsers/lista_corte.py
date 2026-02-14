# services/parsers/lista_corte.py
"""Extrae filas de la Lista de Corte (Dimensiones Netas) del PDF."""

from __future__ import annotations

import re

from ...domain.models import CorteRow


def parse_lista_corte(texto_paginas: str) -> list[CorteRow]:
    """
    Localiza el bloque Lista de Corte y devuelve una CorteRow por cada fila de datos.
    Las líneas que son solo nombre de mueble (ej. "alacena tati") marcan el grupo siguiente.
    """
    bloques = _extraer_bloques_lista_corte(texto_paginas)
    filas: list[CorteRow] = []
    for bloque in bloques:
        lineas = [ln.strip() for ln in bloque.splitlines() if ln.strip()]
        mueble_actual = ""
        anterior_era_fecha = False
        for linea in lineas:
            if _es_encabezado_pagina(linea, anterior_era_fecha):
                anterior_era_fecha = _es_linea_fecha(linea)
                continue
            anterior_era_fecha = _es_linea_fecha(linea)
            if _es_titulo_seccion(linea):
                continue
            if _es_encabezado(linea):
                continue
            if _es_solo_nombre_mueble(linea):
                mueble_actual = linea
                anterior_era_fecha = False
                continue
            row = _parsear_linea_corte(linea, mueble_actual)
            if row is not None:
                filas.append(row)
            anterior_era_fecha = _es_linea_fecha(linea)
    return filas


def _extraer_bloques_lista_corte(texto: str) -> list[str]:
    """Encuentra cada bloque 'Lista de Corte (Dimensiones Netas)...' hasta el siguiente título o fin."""
    patron = re.compile(
        r"Lista de Corte \(Dimensiones Netas\)(?:\s*\(Siguiente\))?\s*\n(.*?)(?=Resumen|Lista de Muebles|$)",
        re.DOTALL | re.IGNORECASE,
    )
    return patron.findall(texto)


# Títulos de sección que se repiten tras salto de página; no son mueble ni dato.
_TITULOS_LISTA_CORTE = (
    "Lista de Corte (Dimensiones Netas)",
    "Lista de Corte (Dimensiones Netas) (Siguiente)",
)


def _es_titulo_seccion(linea: str) -> bool:
    """Línea que es título de sección (descartar, no usar como mueble ni como fila)."""
    ln = (linea or "").strip()
    return ln in _TITULOS_LISTA_CORTE


# Encabezado de cada página del PDF: versión PolyBoard, fecha, nombre proyecto, "Página N/M"
_PATRON_POLYBOARD = re.compile(r"PolyBoard\s+\d+\.\d+", re.IGNORECASE)
_PATRON_PAGINA = re.compile(r"^Página\s+\d+/\d+\s*$", re.IGNORECASE)
_PATRON_FECHA = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}\s*$")


def _es_linea_fecha(linea: str) -> bool:
    """True si la línea es solo una fecha (dd/mm/yyyy)."""
    return bool(linea and _PATRON_FECHA.match(linea.strip()))


def _es_encabezado_pagina(linea: str, anterior_era_fecha: bool) -> bool:
    """
    True si la línea es parte del encabezado de página: PolyBoard, fecha,
    nombre del proyecto o "Página N/M". anterior_era_fecha: la línea previa era fecha
    (para detectar el nombre del proyecto justo después).
    """
    ln = (linea or "").strip()
    if not ln:
        return True
    if _PATRON_POLYBOARD.search(ln):
        return True
    if _PATRON_FECHA.match(ln):
        return True
    if _PATRON_PAGINA.match(ln):
        return True
    if anterior_era_fecha and not re.search(r"\d", ln):
        return True
    return False


def _es_encabezado(linea: str) -> bool:
    """Línea de encabezado de tabla (Material Referencia Altura...)."""
    if not linea:
        return True
    if "Material" in linea and "Referencia" in linea and "Altura" in linea:
        return True
    if "Alture" in linea or ("Anchura" in linea and "Cantidad" in linea):
        return True
    return False


def _es_solo_nombre_mueble(linea: str) -> bool:
    """Línea que es solo nombre de mueble (sin triple altura anchura cantidad)."""
    return bool(linea and not re.search(r"\d+\.?\d*\s+\d+\.?\d*\s+\d+\b", linea))


def _parsear_linea_corte(linea: str, mueble: str) -> CorteRow | None:
    """De una línea de datos obtiene Material, Referencia, Altura, Anchura, Cantidad y cantos."""
    # Buscar triple: float float int (altura anchura cantidad)
    triple = re.search(r"(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+)\s+(.+)$", linea)
    if not triple:
        return None
    altura_s = triple.group(1)
    anchura_s = triple.group(2)
    cantidad_s = triple.group(3)
    resto = triple.group(4).strip()

    try:
        altura = float(altura_s)
        anchura = float(anchura_s)
        cantidad = int(cantidad_s)
    except ValueError:
        return None

    # Resto = "No PAPIER, 0.... PAPIER, 0.... ..." o similar → fibra + 4 cantos
    tokens_resto = resto.split()
    # Fibra suele ser "No" o "Sí"; luego 4 valores de canto (pueden tener comas)
    if len(tokens_resto) >= 5:
        canto_izq = tokens_resto[1] if len(tokens_resto) > 1 else ""
        canto_der = tokens_resto[2] if len(tokens_resto) > 2 else ""
        canto_inf = tokens_resto[3] if len(tokens_resto) > 3 else ""
        canto_sup = tokens_resto[4] if len(tokens_resto) > 4 else ""
    else:
        canto_izq = canto_der = canto_inf = canto_sup = ""

    # Parte anterior a los números: "gris sombr... Estante Fij..." → material + referencia
    pre = linea[: triple.start()].strip()
    material, referencia = _separar_material_referencia(pre)

    return CorteRow(
        material=material,
        referencia=referencia,
        mueble=mueble,
        altura_mm=altura,
        anchura_mm=anchura,
        cantidad=cantidad,
        canto_izq=canto_izq,
        canto_der=canto_der,
        canto_inf=canto_inf,
        canto_sup=canto_sup,
    )


def _separar_material_referencia(pre: str) -> tuple[str, str]:
    """
    Separa 'material referencia' en dos.
    En el PDF ambas columnas pueden terminar en "..."; el material es hasta el primer token que termina en "...".
    """
    tokens = pre.split()
    if not tokens:
        return "", ""
    if len(tokens) == 1:
        return tokens[0], ""
    # Primer token que termina en "..." cierra la columna Material; el resto es Referencia.
    for i, t in enumerate(tokens):
        if t.endswith("..."):
            material = " ".join(tokens[: i + 1])
            referencia = " ".join(tokens[i + 1 :]) if i + 1 < len(tokens) else ""
            return material, referencia
    # Sin "...": primera palabra = material, resto = referencia
    return tokens[0], " ".join(tokens[1:])
