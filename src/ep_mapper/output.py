from __future__ import annotations
from pathlib import Path
from ep_mapper.schema import DeviceMetadata, EpRow

_REGULATION_VERSION = "C70 (F2026C00240, 21 Mar 2026)"
_REGULATION_NAME = "Sch 1, TG(MD)R 2002"

_DISCLAIMER = (
    "DISCLAIMER: This output is a documentation gap analysis only. "
    "It does not assess evidence adequacy, constitute a regulatory determination, "
    "or replace professional review before TGA submission."
)

_COVERAGE_SYMBOLS = {"covered": "✓", "partial": "~", "gap": "✗"}
_CONF_LABEL = {"high": "HIGH", "medium": "MED", "low": "LOW"}


def _ep_section(row: EpRow) -> str:
    lines = [
        f"\nEP {row.ep_number}: {row.ep_title}",
        f"  Citation:       {row.citation}",
    ]
    if row.applicability == "not_applicable":
        lines.append(f"  Status:         NOT APPLICABLE — {row.applicability_basis}")
        return "\n".join(lines)

    symbol = _COVERAGE_SYMBOLS.get(row.coverage_rating, "?")
    conf = _CONF_LABEL.get(row.confidence, row.confidence)
    lines.append(f"  Coverage:       {symbol} {row.coverage_rating.upper()} (confidence: {conf})")

    if row.requires_professional_review:
        lines.append("  *** REQUIRES PROFESSIONAL REVIEW ***")

    if row.evidence_refs:
        lines.append("  Evidence refs:")
        for ref in row.evidence_refs:
            lines.append(f"    - \"{ref}\"")
    else:
        lines.append("  Evidence refs:  (none)")

    if row.gap_notes:
        lines.append(f"  Gap notes:      {row.gap_notes}")

    if row.compliance_deadline:
        lines.append(f"  UDI deadline:   {row.compliance_deadline}")

    if row.structured_extraction:
        lines.append("  Sub-requirements:")
        for sub_req, signal in row.structured_extraction.items():
            lines.append(f"    {sub_req}: {signal or 'not addressed'}")

    return "\n".join(lines)


def format_gap_matrix(
    rows: list[EpRow],
    meta: DeviceMetadata,
    pdf_path: Path,
    page_count: int,
    disclaimer_timestamp: str,
) -> str:
    ivd_label = "IVD" if meta.ivd else "non-IVD"
    active_label = "active" if meta.active else "passive"

    header = "\n".join([
        "=" * 72,
        "TGA ESSENTIAL PRINCIPLES GAP ANALYSIS",
        "=" * 72,
        f"Regulation:       {_REGULATION_NAME}, {_REGULATION_VERSION}",
        f"Device:           {meta.device_name} — Class {meta.device_class}, {ivd_label}, {active_label}",
        f"Intended purpose: {meta.intended_purpose}",
        f"Document:         {pdf_path.name} ({page_count} pages)",
        f"Acknowledged:     {disclaimer_timestamp}",
        "",
        _DISCLAIMER,
        "=" * 72,
    ])

    ep_sections = "\n".join(_ep_section(r) for r in rows)

    applicable = [r for r in rows if r.applicability == "applicable"]
    covered = sum(1 for r in applicable if r.coverage_rating == "covered")
    partial = sum(1 for r in applicable if r.coverage_rating == "partial")
    gap = sum(1 for r in applicable if r.coverage_rating == "gap")
    not_applicable = sum(1 for r in rows if r.applicability == "not_applicable")

    summary = "\n".join([
        "",
        "=" * 72,
        "SUMMARY",
        "=" * 72,
        f"  Applicable EPs:     {len(applicable)}",
        f"    Covered:          {covered}",
        f"    Partial:          {partial}",
        f"    Gap:              {gap}",
        f"  Not applicable:     {not_applicable}",
        "",
        "  EPs requiring professional review:",
    ])
    review_eps = [r for r in applicable if r.requires_professional_review]
    if review_eps:
        for r in review_eps:
            summary += f"\n    EP {r.ep_number}: {r.ep_title}"
    else:
        summary += "\n    (none)"
    summary += "\n" + "=" * 72

    return "\n".join([header, ep_sections, summary])
