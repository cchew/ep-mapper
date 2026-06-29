"""Integration test: full pipeline with mocked LLM, real PDFs, real lex-au XML.

Requires TG(MD)R 2002 XML to be present in lex-au corpus (Task 0 gate must have passed).
LEX_AU_CORPUS_DIR defaults to ../../lex-au/repo/corpus.
"""
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from ep_mapper.schema import DeviceMetadata


def _find_lex_au_xml() -> Path | None:
    import glob
    corpus_dir = Path(os.environ.get("LEX_AU_CORPUS_DIR", "../../lex-au/repo/corpus"))
    matches = list(glob.glob(str(corpus_dir / "xml" / "*therapeutic*")))
    return Path(sorted(matches)[0]) if matches else None


@pytest.fixture(scope="session")
def lex_au_xml() -> Path:
    xml = _find_lex_au_xml()
    if xml is None:
        pytest.skip("TG(MD)R 2002 XML not found — run Task 0 first")
    return xml


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def _mock_covered_response(ep_num: str) -> MagicMock:
    data = {
        "coverage_rating": "covered",
        "evidence_refs": [f"Evidence addressing EP {ep_num} is documented in this section."],
        "gap_notes": None,
        "confidence": "high",
    }
    response = MagicMock()
    response.content = [MagicMock(text=json.dumps(data))]
    return response


def test_scenario1_class_i_not_applicable_eps(lex_au_xml, fixtures_dir):
    """Scenario 1: Class I passive device. EP 11, 12, 13A, 13B, 15 not applicable."""
    from ep_mapper.pipeline import run_analysis

    meta = DeviceMetadata("SimpStrap Pro", "Minor wound care", "I", False, False, False, False, False)
    pdf_path = fixtures_dir / "scenario1_class_i.pdf"

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_covered_response("generic")

    with patch("ep_mapper.pipeline.anthropic.Anthropic", return_value=mock_client):
        rows, pages, page_count = run_analysis(pdf_path, meta, lex_au_xml, "2026-06-29T12:00:00")

    not_applicable_nums = {r.ep_number for r in rows if r.applicability == "not_applicable"}
    assert "11" in not_applicable_nums
    assert "12" in not_applicable_nums
    assert "13A" in not_applicable_nums
    assert "13B" in not_applicable_nums
    assert "15" in not_applicable_nums

    applicable = [r for r in rows if r.applicability == "applicable"]
    assert len(applicable) > 0
    assert page_count == 3


def test_scenario2_class_iia_ep13c_has_deadline(lex_au_xml, fixtures_dir):
    """Scenario 2: Class IIa — EP 13C compliance deadline is 1 July 2028."""
    from ep_mapper.pipeline import run_analysis

    meta = DeviceMetadata("VenaFlow 3000", "IV medication delivery", "IIa", False, True, False, False, True)
    pdf_path = fixtures_dir / "scenario2_class_iia.pdf"

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_covered_response("generic")

    with patch("ep_mapper.pipeline.anthropic.Anthropic", return_value=mock_client):
        rows, _, _ = run_analysis(pdf_path, meta, lex_au_xml, "2026-06-29T12:00:00")

    ep13c = next((r for r in rows if r.ep_number == "13C"), None)
    assert ep13c is not None
    assert ep13c.applicability == "applicable"
    assert ep13c.compliance_deadline is not None
    assert "2028" in ep13c.compliance_deadline


def test_scenario3_class_iib_ep14_requires_review(lex_au_xml, fixtures_dir):
    """Scenario 3: EP 14 always requires professional review."""
    from ep_mapper.pipeline import run_analysis

    meta = DeviceMetadata("NeuroPace X1", "Neural stimulation for epilepsy", "IIb", False, True, True, False, True)
    pdf_path = fixtures_dir / "scenario3_class_iib.pdf"

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_covered_response("generic")

    with patch("ep_mapper.pipeline.anthropic.Anthropic", return_value=mock_client):
        rows, _, _ = run_analysis(pdf_path, meta, lex_au_xml, "2026-06-29T12:00:00")

    ep14 = next((r for r in rows if r.ep_number == "14"), None)
    assert ep14 is not None
    assert ep14.requires_professional_review is True

    ep13c = next((r for r in rows if r.ep_number == "13C"), None)
    assert ep13c is not None
    assert "2027" in ep13c.compliance_deadline


def test_full_output_contains_regulation_version(lex_au_xml, fixtures_dir):
    """Output header must contain C70 (F2026C00240) in every run."""
    from ep_mapper.pipeline import run_analysis
    from ep_mapper.output import format_gap_matrix

    meta = DeviceMetadata("SimpStrap Pro", "Minor wound care", "I", False, False, False, False, False)
    pdf_path = fixtures_dir / "scenario1_class_i.pdf"

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_covered_response("generic")

    with patch("ep_mapper.pipeline.anthropic.Anthropic", return_value=mock_client):
        rows, pages, page_count = run_analysis(pdf_path, meta, lex_au_xml, "2026-06-29T12:00:00")

    output = format_gap_matrix(rows, meta, pdf_path, page_count, "2026-06-29T12:00:00")
    assert "F2026C00240" in output
    assert "C70" in output
    assert "21 Mar 2026" in output
