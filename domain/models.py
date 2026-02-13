from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PdfDocument:
    path: Path
    pages: list[str]


@dataclass(frozen=True)
class ParsedRow:
    line_number: int
    raw_text: str
    fields: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ParsedData:
    rows: list[ParsedRow]


@dataclass(frozen=True)
class ExcelRow:
    values: tuple[str, ...]


@dataclass(frozen=True)
class TransformationResult:
    headers: tuple[str, ...]
    rows: list[ExcelRow]


@dataclass(frozen=True)
class ProcessResult:
    ok: bool
    file_path: str | None
    errors: list[str]

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "file_path": self.file_path,
            "errors": self.errors,
        }
