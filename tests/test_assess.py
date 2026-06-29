import json
from unittest.mock import MagicMock
import pytest
from ep_mapper.schema import EpClause, DeviceMetadata
from ep_mapper.assess import (
    build_assessment_prompt,
    verify_passages,
    assess_ep,
)

EP1 = EpClause(
    ep_number="1",
    ep_title="Use of medical devices not to compromise health and safety",
    text="A medical device must be safe and not compromise health and safety.",
    citation="Essential Principle 1, Schedule 1, Therapeutic Goods (Medical Devices) Regulations 2002",
    citation_uri="//schedule-1__clause-1",
)

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

DOCUMENT_TEXT = "The InfuPro 200 has been designed to ensure patient safety. Risk management has been conducted per ISO 14971."


def test_build_prompt_contains_ep_text():
    prompt = build_assessment_prompt(EP1, META, DOCUMENT_TEXT, sub_requirements=None)
    assert "Essential Principle 1" in prompt
    assert "InfuPro 200" in prompt
    assert "IV medication delivery" in prompt
    assert DOCUMENT_TEXT in prompt


def test_build_prompt_includes_sub_requirements():
    sub_reqs = ["Biocompatibility testing per ISO 10993", "Toxicity data documented"]
    prompt = build_assessment_prompt(EP1, META, DOCUMENT_TEXT, sub_requirements=sub_reqs)
    assert "Biocompatibility testing" in prompt
    assert "TGA Guidance" in prompt


def test_verify_passages_found():
    refs = ["designed to ensure patient safety"]
    result = verify_passages(refs, DOCUMENT_TEXT)
    assert result == ["designed to ensure patient safety"]


def test_verify_passages_not_found_adds_unverified():
    refs = ["This text does not exist in the document at all"]
    result = verify_passages(refs, DOCUMENT_TEXT)
    assert result[0].endswith("[unverified]")


def test_verify_passages_normalises_whitespace():
    refs = ["designed  to  ensure   patient  safety"]
    result = verify_passages(refs, DOCUMENT_TEXT)
    assert "[unverified]" not in result[0]


def test_assess_ep_returns_ep_row(monkeypatch):
    from ep_mapper.schema import EpRow

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "coverage_rating": "covered",
        "evidence_refs": ["designed to ensure patient safety"],
        "gap_notes": None,
        "confidence": "high",
    }))]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    row = assess_ep(
        clause=EP1,
        device_meta=META,
        document_text=DOCUMENT_TEXT,
        sub_requirements=None,
        client=mock_client,
        applicability="applicable",
        applicability_basis=None,
    )
    assert isinstance(row, EpRow)
    assert row.coverage_rating == "covered"
    assert row.ep_number == "1"
    assert row.requires_professional_review is False


def test_assess_ep_ep14_always_requires_review():
    ep14 = EpClause(
        ep_number="14",
        ep_title="Clinical evidence",
        text="Clinical evidence must be provided.",
        citation="Essential Principle 14, Schedule 1, Therapeutic Goods (Medical Devices) Regulations 2002",
        citation_uri="//schedule-1__clause-14",
    )

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "coverage_rating": "partial",
        "evidence_refs": [],
        "gap_notes": "No clinical data provided",
        "confidence": "low",
    }))]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    row = assess_ep(
        clause=ep14,
        device_meta=META,
        document_text=DOCUMENT_TEXT,
        sub_requirements=None,
        client=mock_client,
        applicability="applicable",
        applicability_basis=None,
    )
    assert row.requires_professional_review is True


def test_assess_ep_unverified_lowers_confidence():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "coverage_rating": "covered",
        "evidence_refs": ["This passage does not exist in the actual document"],
        "gap_notes": None,
        "confidence": "high",
    }))]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    row = assess_ep(
        clause=EP1,
        device_meta=META,
        document_text=DOCUMENT_TEXT,
        sub_requirements=None,
        client=mock_client,
        applicability="applicable",
        applicability_basis=None,
    )
    assert row.confidence == "low"
    assert "[unverified]" in row.evidence_refs[0]
