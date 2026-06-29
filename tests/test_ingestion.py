from pathlib import Path
import pytest


def _make_test_pdf(tmp_path: Path, pages: list[str]) -> Path:
    """Create a minimal multi-page PDF using reportlab."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    pdf_path = tmp_path / "test.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    for page_text in pages:
        c.drawString(72, 700, page_text)
        c.showPage()
    c.save()
    return pdf_path


def test_pdf_to_pages_returns_list(tmp_path):
    from ep_mapper.ingestion import pdf_to_pages
    pdf = _make_test_pdf(tmp_path, ["Page one content", "Page two content"])
    result = pdf_to_pages(pdf)
    assert isinstance(result, list)
    assert len(result) == 2


def test_pdf_to_pages_text_present(tmp_path):
    from ep_mapper.ingestion import pdf_to_pages
    pdf = _make_test_pdf(tmp_path, ["Biocompatibility testing performed per ISO 10993."])
    result = pdf_to_pages(pdf)
    assert len(result) == 1
    assert "Biocompatibility" in result[0]


def test_pages_to_document_text(tmp_path):
    from ep_mapper.ingestion import pages_to_document_text
    pages = ["Page one text", "Page two text"]
    combined = pages_to_document_text(pages)
    assert "Page one text" in combined
    assert "Page two text" in combined
    assert "--- Page 1 ---" in combined
    assert "--- Page 2 ---" in combined


def test_pdf_not_found_raises(tmp_path):
    from ep_mapper.ingestion import pdf_to_pages
    with pytest.raises(FileNotFoundError):
        pdf_to_pages(tmp_path / "missing.pdf")
