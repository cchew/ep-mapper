from ep_mapper.schema import DeviceMetadata, EpClause, EpRow


def test_device_metadata_defaults():
    m = DeviceMetadata(
        device_name="InfuPro 200",
        intended_purpose="IV medication delivery",
        device_class="IIa",
        ivd=False,
        active=True,
        implantable=False,
        radiation=False,
        software=True,
    )
    assert m.device_class == "IIa"
    assert m.software is True
    assert m.implantable is False


def test_ep_clause_fields():
    c = EpClause(
        ep_number="7.3",
        ep_title="Chemical, physical and biological properties",
        text="The device must not contain toxic materials...",
        citation="Essential Principle 7.3, Schedule 1, Therapeutic Goods (Medical Devices) Regulations 2002",
        citation_uri="/akn/au/regulation/2002/0/schedule-1/clause-7/subclause-7-3",
    )
    assert c.ep_number == "7.3"
    assert "Essential Principle 7.3" in c.citation


def test_ep_row_not_applicable():
    row = EpRow(
        ep_number="15",
        ep_title="Principles applying to IVD medical devices only",
        citation="Essential Principle 15, Schedule 1, Therapeutic Goods (Medical Devices) Regulations 2002",
        citation_uri="/akn/au/regulation/2002/0/schedule-1/clause-15",
        applicability="not_applicable",
        applicability_basis="Sch 1, cl 15 — applies to IVD devices only; device is non-IVD",
        coverage_rating="gap",
        evidence_refs=[],
        gap_notes=None,
        confidence="high",
        requires_professional_review=False,
        structured_extraction=None,
        compliance_deadline=None,
    )
    assert row.applicability == "not_applicable"
    assert row.applicability_basis is not None


def test_ep_row_requires_professional_review_default():
    row = EpRow(
        ep_number="14",
        ep_title="Clinical evidence",
        citation="Essential Principle 14, Schedule 1, Therapeutic Goods (Medical Devices) Regulations 2002",
        citation_uri="/akn/au/regulation/2002/0/schedule-1/clause-14",
        applicability="applicable",
        applicability_basis=None,
        coverage_rating="partial",
        evidence_refs=["The clinical evaluation report demonstrates..."],
        gap_notes="Post-market surveillance plan not addressed",
        confidence="medium",
        requires_professional_review=True,
        structured_extraction=None,
        compliance_deadline=None,
    )
    assert row.requires_professional_review is True
