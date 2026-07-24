from pathlib import Path
from ep_mapper.schema import DeviceMetadata, EpRow
from ep_mapper.output import format_gap_matrix

META = DeviceMetadata(
    device_name="InfuPro 200",
    intended_purpose="IV medication delivery in hospital settings",
    device_class="IIa",
    ivd=False,
    active=True,
    implantable=False,
    radiation=False,
    software=True,
)

ROWS = [
    EpRow(
        ep_number="1",
        ep_title="Use of medical devices not to compromise health and safety",
        citation="Essential Principle 1, Schedule 1, Therapeutic Goods (Medical Devices) Regulations 2002",
        citation_uri="//schedule-1__clause-1",
        applicability="applicable",
        applicability_basis=None,
        coverage_rating="covered",
        evidence_refs=["Risk management per ISO 14971 documented in Section 3."],
        gap_notes=None,
        confidence="high",
        requires_professional_review=False,
        structured_extraction=None,
        compliance_deadline=None,
    ),
    EpRow(
        ep_number="13C",
        ep_title="Unique Device Identification (UDI)",
        citation="Essential Principle 13C, Schedule 1, Therapeutic Goods (Medical Devices) Regulations 2002",
        citation_uri="//schedule-1__clause-13c",
        applicability="applicable",
        applicability_basis=None,
        coverage_rating="gap",
        evidence_refs=[],
        gap_notes="No UDI documentation found in evidence document.",
        confidence="high",
        requires_professional_review=False,
        structured_extraction=None,
        compliance_deadline="Class IIa devices: 1 July 2028",
    ),
    EpRow(
        ep_number="15",
        ep_title="Principles applying to IVD medical devices only",
        citation="Essential Principle 15, Schedule 1, Therapeutic Goods (Medical Devices) Regulations 2002",
        citation_uri="//schedule-1__clause-15",
        applicability="not_applicable",
        applicability_basis="Sch 1, cl 15 — applies to IVD devices only; device is non-IVD",
        coverage_rating="gap",
        evidence_refs=[],
        gap_notes=None,
        confidence="high",
        requires_professional_review=False,
        structured_extraction=None,
        compliance_deadline=None,
    ),
]

TIMESTAMP = "2026-06-29T14:30:00"


def test_output_contains_regulation_header():
    out = format_gap_matrix(ROWS, META, Path("evidence.pdf"), 5, TIMESTAMP)
    assert "F2026C00610" in out
    assert "C71" in out
    assert "1 Jul 2026" in out


def test_output_contains_device_info():
    out = format_gap_matrix(ROWS, META, Path("evidence.pdf"), 5, TIMESTAMP)
    assert "InfuPro 200" in out
    assert "IIa" in out
    assert "IV medication delivery" in out


def test_output_contains_disclaimer_timestamp():
    out = format_gap_matrix(ROWS, META, Path("evidence.pdf"), 5, TIMESTAMP)
    assert TIMESTAMP in out


def test_output_ep1_covered():
    out = format_gap_matrix(ROWS, META, Path("evidence.pdf"), 5, TIMESTAMP)
    assert "EP 1" in out
    assert "COVERED" in out.upper() or "covered" in out.lower()


def test_output_ep13c_gap_with_deadline():
    out = format_gap_matrix(ROWS, META, Path("evidence.pdf"), 5, TIMESTAMP)
    assert "13C" in out
    assert "GAP" in out.upper() or "gap" in out.lower()
    assert "1 July 2028" in out


def test_output_not_applicable_shows_basis():
    out = format_gap_matrix(ROWS, META, Path("evidence.pdf"), 5, TIMESTAMP)
    assert "NOT APPLICABLE" in out.upper() or "not_applicable" in out.lower()
    assert "IVD" in out


def test_output_summary_table():
    out = format_gap_matrix(ROWS, META, Path("evidence.pdf"), 5, TIMESTAMP)
    assert "SUMMARY" in out.upper()


def test_output_disclaimer_text():
    out = format_gap_matrix(ROWS, META, Path("evidence.pdf"), 5, TIMESTAMP)
    assert "documentation gap analysis" in out.lower()
    assert "does not assess evidence adequacy" in out.lower() or "not assess" in out.lower()
