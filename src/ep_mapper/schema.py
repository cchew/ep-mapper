from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DeviceMetadata:
    device_name: str
    intended_purpose: str
    device_class: Literal["I", "IIa", "IIb", "III"]
    ivd: bool
    active: bool
    implantable: bool
    radiation: bool
    software: bool


@dataclass
class EpClause:
    ep_number: str
    ep_title: str
    text: str
    citation: str
    citation_uri: str


@dataclass
class EpRow:
    ep_number: str
    ep_title: str
    citation: str
    citation_uri: str
    applicability: Literal["applicable", "not_applicable"]
    applicability_basis: str | None
    coverage_rating: Literal["covered", "partial", "gap"]
    evidence_refs: list[str]
    gap_notes: str | None
    confidence: Literal["high", "medium", "low"]
    requires_professional_review: bool
    structured_extraction: dict | None
    compliance_deadline: str | None
