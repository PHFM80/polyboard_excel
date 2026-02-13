from __future__ import annotations

from ..domain.models import ExcelRow, ParsedData, TransformationResult


class DataTransformer:
    def transform(self, parsed_data: ParsedData) -> TransformationResult:
        raise NotImplementedError


class ProviderExcelTransformer(DataTransformer):
    """Maps parsed rows to a tabular format ready for Excel export."""

    def transform(self, parsed_data: ParsedData) -> TransformationResult:
        headers = ("line_number", "raw_text", "fields")
        rows: list[ExcelRow] = []

        for row in parsed_data.rows:
            rows.append(
                ExcelRow(
                    values=(
                        str(row.line_number),
                        row.raw_text,
                        " | ".join(row.fields),
                    )
                )
            )

        return TransformationResult(headers=headers, rows=rows)
