from __future__ import annotations

import re

from ..domain.models import ParsedData, ParsedRow, PdfDocument


class PdfParser:
    def parse(self, document: PdfDocument) -> ParsedData:
        raise NotImplementedError


class PolyboardPdfParser(PdfParser):
    """Converts extracted text into neutral parsed rows."""

    _split_pattern = re.compile(r"\s*[|;\t]\s*")

    def parse(self, document: PdfDocument) -> ParsedData:
        rows: list[ParsedRow] = []

        line_number = 1
        for page_text in document.pages:
            for line in page_text.splitlines():
                normalized = line.strip()
                if not normalized:
                    continue

                fields = tuple(self._split_pattern.split(normalized))
                if not fields:
                    fields = (normalized,)

                rows.append(
                    ParsedRow(
                        line_number=line_number,
                        raw_text=normalized,
                        fields=fields,
                    )
                )
                line_number += 1

        return ParsedData(rows=rows)
