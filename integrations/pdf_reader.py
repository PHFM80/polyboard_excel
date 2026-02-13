from __future__ import annotations

from pathlib import Path

from ..domain.models import PdfDocument


class PdfReader:
    def read(self, pdf_path: Path) -> PdfDocument:
        raise NotImplementedError


class PypdfPdfReader(PdfReader):
    """PDF integration isolated from service orchestration."""

    def read(self, pdf_path: Path) -> PdfDocument:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            from pypdf import PdfReader as _PdfReader
        except ImportError as exc:
            raise RuntimeError("Missing dependency 'pypdf'. Install it to read PDF files.") from exc

        reader = _PdfReader(str(pdf_path))
        pages: list[str] = []
        for page in reader.pages:
            pages.append((page.extract_text() or "").strip())

        return PdfDocument(path=pdf_path, pages=pages)
