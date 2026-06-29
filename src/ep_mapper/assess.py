from __future__ import annotations
import json
import re

import anthropic

from ep_mapper.schema import DeviceMetadata, EpClause, EpRow

_ALWAYS_REVIEW_EPS = {"7", "12", "14"}

_SYSTEM_PROMPT = (
    "You are a regulatory affairs assistant analysing medical device documentation against "
    "Australian Essential Principles (Schedule 1, TG(MD)R 2002). "
    "Quote evidence verbatim from the manufacturer document. "
    "Return ONLY valid JSON — no markdown fences, no commentary."
)

_JSON_SCHEMA_HINT = (
    '{"coverage_rating": "covered|partial|gap", '
    '"evidence_refs": ["verbatim quoted passage from document", ...], '
    '"gap_notes": "what is missing or insufficient, or null", '
    '"confidence": "high|medium|low"}'
)

_STRUCTURED_JSON_SCHEMA_HINT = (
    '{"coverage_rating": "covered|partial|gap", '
    '"evidence_refs": ["verbatim quoted passage from document", ...], '
    '"gap_notes": "what is missing or null", '
    '"confidence": "high|medium|low", '
    '"structured_extraction": {"sub_requirement_label": "signal from document or null", ...}}'
)


def _normalise(text: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation for substring matching."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def verify_passages(evidence_refs: list[str], document_text: str) -> list[str]:
    """Check each quoted passage exists in the source document.

    Returns refs unchanged if found, or with '[unverified]' appended if not.
    """
    normalised_doc = _normalise(document_text)
    result = []
    for ref in evidence_refs:
        normalised_ref = _normalise(ref)
        if normalised_ref and normalised_ref in normalised_doc:
            result.append(ref)
        else:
            result.append(f"{ref} [unverified]")
    return result


def build_assessment_prompt(
    clause: EpClause,
    device_meta: DeviceMetadata,
    document_text: str,
    sub_requirements: list[str] | None,
) -> str:
    parts = [
        "## Device Under Assessment",
        f"Name: {device_meta.device_name}",
        f"Intended Purpose: {device_meta.intended_purpose}",
        f"Class: {device_meta.device_class} | IVD: {device_meta.ivd} | Active: {device_meta.active}",
        "",
        f"## Essential Principle {clause.ep_number}: {clause.ep_title}",
        f"Citation: {clause.citation}",
        "",
        "### Legislative Text",
        clause.text,
    ]

    if sub_requirements:
        parts += [
            "",
            "### TGA Guidance Sub-Requirements (guidance only, not legislative)",
            *[f"- {req}" for req in sub_requirements],
        ]
        schema_hint = _STRUCTURED_JSON_SCHEMA_HINT
    else:
        schema_hint = _JSON_SCHEMA_HINT

    parts += [
        "",
        "### Manufacturer Evidence Document",
        document_text,
        "",
        "### Task",
        "Assess whether the evidence document addresses this Essential Principle.",
        "Quote verbatim passages from the document as evidence_refs.",
        "Return ONLY this JSON schema:",
        schema_hint,
    ]
    return "\n".join(parts)


def _default_model() -> str:
    import os
    return os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def _error_row(
    clause: EpClause,
    applicability: str,
    applicability_basis: str | None,
    compliance_deadline: str | None,
    reason: str,
) -> EpRow:
    return EpRow(
        ep_number=clause.ep_number,
        ep_title=clause.ep_title,
        citation=clause.citation,
        citation_uri=clause.citation_uri,
        applicability=applicability,
        applicability_basis=applicability_basis,
        coverage_rating="gap",
        evidence_refs=[],
        gap_notes=f"Assessment failed: {reason}",
        confidence="low",
        requires_professional_review=True,
        structured_extraction=None,
        compliance_deadline=compliance_deadline,
    )


def assess_ep(
    clause: EpClause,
    device_meta: DeviceMetadata,
    document_text: str,
    sub_requirements: list[str] | None,
    client: anthropic.Anthropic,
    applicability: str,
    applicability_basis: str | None,
    compliance_deadline: str | None = None,
) -> EpRow:
    """Run LLM coverage assessment for one EP/sub-clause and return an EpRow."""
    prompt = build_assessment_prompt(clause, device_meta, document_text, sub_requirements)

    try:
        response = client.messages.create(
            model=_default_model(),
            max_tokens=2048,
            temperature=0,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as e:
        return _error_row(clause, applicability, applicability_basis, compliance_deadline, str(e))

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```json\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return _error_row(clause, applicability, applicability_basis, compliance_deadline, f"JSON decode error: {e}")

    evidence_refs: list[str] = data.get("evidence_refs", [])
    grounded_refs = verify_passages(evidence_refs, document_text)

    confidence = data.get("confidence", "low")
    if any("[unverified]" in r for r in grounded_refs):
        confidence = "low"

    requires_review = clause.ep_number in _ALWAYS_REVIEW_EPS

    return EpRow(
        ep_number=clause.ep_number,
        ep_title=clause.ep_title,
        citation=clause.citation,
        citation_uri=clause.citation_uri,
        applicability=applicability,
        applicability_basis=applicability_basis,
        coverage_rating=data.get("coverage_rating", "gap"),
        evidence_refs=grounded_refs,
        gap_notes=data.get("gap_notes"),
        confidence=confidence,
        requires_professional_review=requires_review,
        structured_extraction=data.get("structured_extraction"),
        compliance_deadline=compliance_deadline,
    )
