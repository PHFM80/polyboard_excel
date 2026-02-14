# service.py
"""Fachada pública del módulo Polyboard → Excel."""

from __future__ import annotations

from pathlib import Path

from .domain.models import ProcessResult
from .integrations.excel_writer import write_excel, write_excel_from_template
from .integrations.pdf_reader import read_pages
from .utils.filename_with_date import add_date_to_filename
from .services.parser import parse_pages
from .services.transformer import to_provider_rows

# Plantilla por defecto (junto al paquete); si existe se usa cuando template_path es None.
_DEFAULT_TEMPLATE = Path(__file__).resolve().parent / "plantilla" / "PLANILLA PEDIDOS ONLINE.xlsx"


class PolyboardExcelService:
    """
    Fachada principal del módulo.
    Orquesta el proceso completo:
    PDF → extracción → transformación → generación Excel
    """

    def process(
        self,
        pdf_path: str,
        output_path: str | None = None,
        template_path: str | None = None,
    ) -> dict[str, bool | str | None | list[str]]:
        """
        Procesa un PDF de Polyboard y genera un Excel para proveedor.

        Args:
            pdf_path: Ruta del archivo PDF.
            output_path: Ruta del Excel a generar. Si es None, se usa el mismo
                nombre que el PDF con extensión .xlsx en el mismo directorio.
            template_path: Ruta de la plantilla .xlsx. Si es None, se usa la de
                plantilla/PLANILLA PEDIDOS ONLINE.xlsx si existe. Con plantilla,
                el archivo se guarda con la fecha en el nombre (ej. archivo_2025-02-13.xlsx).

        Returns:
            dict con:
                - ok (bool)
                - file_path (str | None)
                - errors (list)
        """
        result = self._run(pdf_path, output_path, template_path)
        return {
            "ok": result.ok,
            "file_path": result.file_path,
            "errors": result.errors,
        }

    def _run(
        self,
        pdf_path: str,
        output_path: str | None,
        template_path: str | None,
    ) -> ProcessResult:
        """Ejecuta el flujo y devuelve ProcessResult."""
        if not (pdf_path or "").strip():
            return ProcessResult(
                ok=False,
                file_path=None,
                errors=["PDF path no proporcionado."],
            )

        template = template_path if template_path else (
            str(_DEFAULT_TEMPLATE) if _DEFAULT_TEMPLATE.exists() else None
        )
        resolved_output = output_path or self._default_output_path(pdf_path)
        if template:
            resolved_output = add_date_to_filename(resolved_output)

        try:
            pages_text = read_pages(pdf_path)
        except FileNotFoundError as e:
            return ProcessResult(ok=False, file_path=None, errors=[str(e)])
        except ValueError as e:
            return ProcessResult(ok=False, file_path=None, errors=[str(e)])
        except OSError as e:
            return ProcessResult(ok=False, file_path=None, errors=[str(e)])

        extracted = parse_pages(pages_text)
        rows = to_provider_rows(extracted)

        if not rows:
            return ProcessResult(
                ok=False,
                file_path=None,
                errors=["El PDF no contenía datos para exportar."],
            )

        try:
            if template:
                write_excel_from_template(template, rows, resolved_output)
            else:
                write_excel(rows, resolved_output)
        except (ValueError, OSError, RuntimeError, FileNotFoundError) as e:
            return ProcessResult(
                ok=False,
                file_path=None,
                errors=[str(e)],
            )

        return ProcessResult(
            ok=True,
            file_path=resolved_output,
            errors=[],
        )

    @staticmethod
    def _default_output_path(pdf_path: str) -> str:
        """Genera la ruta del Excel a partir de la ruta del PDF."""
        path = Path(pdf_path)
        return str(path.with_suffix(".xlsx"))
