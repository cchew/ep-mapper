from __future__ import annotations
from pathlib import Path

import anthropic

from ep_mapper.schema import DeviceMetadata, EpRow
from ep_mapper.corpus import load_schedule1
from ep_mapper.guidance import TGA_GUIDANCE
from ep_mapper.applicability import ep_applicability_filter
from ep_mapper.ingestion import pdf_to_pages, pages_to_document_text
from ep_mapper.assess import assess_ep

# Top-level EPs in display order — 18 total
_TOP_LEVEL_EPS = [
    "1", "2", "3", "4", "5", "6",
    "7", "8", "9", "10", "11", "12",
    "13", "13A", "13B", "13C", "14", "15",
]

# EP 13C compliance deadlines by device class (static, per TGA schedule)
_UDI_DEADLINES: dict[str, str] = {
    "III":  "Class III devices: 1 July 2026",
    "IIb":  "Class IIb devices: 1 July 2027",
    "IIa":  "Class IIa devices: 1 July 2028",
    "I":    "Class I devices: TBA (check TGA website)",
}

# EPs with structured sub-requirement extraction (uses TGA_GUIDANCE)
_STRUCTURED_EPS = {"7", "12", "14"}


def run_analysis(
    pdf_path: Path,
    meta: DeviceMetadata,
    lex_au_xml_path: Path,
    disclaimer_timestamp: str,
) -> tuple[list[EpRow], list[str], int]:
    """Run full EP gap analysis. Returns (rows, pages, page_count)."""
    client = anthropic.Anthropic()

    ep_clauses = load_schedule1(lex_au_xml_path)
    pages = pdf_to_pages(pdf_path)
    document_text = pages_to_document_text(pages)

    top_level_in_corpus = [ep for ep in _TOP_LEVEL_EPS if ep in ep_clauses]
    applicability = ep_applicability_filter(meta, top_level_in_corpus)

    rows: list[EpRow] = []

    for ep_num in top_level_in_corpus:
        clause = ep_clauses[ep_num]
        app, app_basis = applicability[ep_num]

        if app == "not_applicable":
            rows.append(EpRow(
                ep_number=ep_num,
                ep_title=clause.ep_title,
                citation=clause.citation,
                citation_uri=clause.citation_uri,
                applicability="not_applicable",
                applicability_basis=app_basis,
                coverage_rating="gap",
                evidence_refs=[],
                gap_notes=None,
                confidence="high",
                requires_professional_review=False,
                structured_extraction=None,
                compliance_deadline=None,
            ))
            continue

        sub_reqs = TGA_GUIDANCE.get(ep_num) if ep_num in _STRUCTURED_EPS else None
        compliance_deadline = _UDI_DEADLINES.get(meta.device_class) if ep_num == "13C" else None

        row = assess_ep(
            clause=clause,
            device_meta=meta,
            document_text=document_text,
            sub_requirements=sub_reqs,
            client=client,
            applicability=app,
            applicability_basis=app_basis,
            compliance_deadline=compliance_deadline,
        )
        rows.append(row)

    return rows, pages, len(pages)
