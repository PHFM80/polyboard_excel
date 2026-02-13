from __future__ import annotations

from pathlib import Path

from ..domain.models import TransformationResult


class ExcelWriter:
    def write(self, data: TransformationResult, output_path: Path) -> Path:
        raise NotImplementedError


class OpenpyxlExcelWriter(ExcelWriter):
    """Excel integration isolated from service orchestration."""

    def write(self, data: TransformationResult, output_path: Path) -> Path:
        try:
            from openpyxl import Workbook
        except ImportError as exc:
            raise RuntimeError("Missing dependency 'openpyxl'. Install it to write Excel files.") from exc

        wb = Workbook()
        ws = wb.active
        ws.title = "polyboard"

        ws.append(list(data.headers))
        for row in data.rows:
            ws.append(list(row.values))

        wb.save(str(output_path))
        return output_path
