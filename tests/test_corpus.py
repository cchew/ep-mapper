from pathlib import Path
from lxml import etree
import pytest
from ep_mapper.corpus import load_schedule1
from ep_mapper.schema import EpClause

AKN_NS = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"
AKN = f"{{{AKN_NS}}}"


def _make_minimal_xml() -> bytes:
    """Build a minimal AKN XML with Schedule 1 having EP 1, EP 7, EP 7.1, and EP 13A."""
    nsmap = {None: AKN_NS}
    root = etree.Element(f"{AKN}akomaNtoso", nsmap=nsmap)
    act = etree.SubElement(root, f"{AKN}act", name="act")
    body = etree.SubElement(act, f"{AKN}body")
    attachments = etree.SubElement(act, f"{AKN}attachments")
    attachment = etree.SubElement(attachments, f"{AKN}attachment")
    schedule = etree.SubElement(attachment, f"{AKN}hcontainer", name="schedule", eId="schedule-1")
    etree.SubElement(schedule, f"{AKN}heading").text = "Essential Principles"

    # EP 1
    cl1 = etree.SubElement(schedule, f"{AKN}hcontainer", name="clause", eId="schedule-1__clause-1")
    etree.SubElement(cl1, f"{AKN}num").text = "1"
    etree.SubElement(cl1, f"{AKN}heading").text = "Use of medical devices not to compromise health and safety"
    content = etree.SubElement(cl1, f"{AKN}content")
    etree.SubElement(content, f"{AKN}p").text = "A medical device must be safe."

    # EP 7 (with subclauses)
    cl7 = etree.SubElement(schedule, f"{AKN}hcontainer", name="clause", eId="schedule-1__clause-7")
    etree.SubElement(cl7, f"{AKN}num").text = "7"
    etree.SubElement(cl7, f"{AKN}heading").text = "Chemical, physical and biological properties"
    sub71 = etree.SubElement(cl7, f"{AKN}hcontainer", name="subclause", eId="schedule-1__clause-7__subclause-7-1")
    etree.SubElement(sub71, f"{AKN}num").text = "7.1"
    c71 = etree.SubElement(sub71, f"{AKN}content")
    etree.SubElement(c71, f"{AKN}p").text = "Materials must not be toxic."

    # EP 13A
    cl13a = etree.SubElement(schedule, f"{AKN}hcontainer", name="clause", eId="schedule-1__clause-13A")
    etree.SubElement(cl13a, f"{AKN}num").text = "13A"
    etree.SubElement(cl13a, f"{AKN}heading").text = "Patient implant card"
    c13a = etree.SubElement(etree.SubElement(cl13a, f"{AKN}content"), f"{AKN}p")
    c13a.text = "An implant card must be provided."

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")


@pytest.fixture
def minimal_xml(tmp_path) -> Path:
    xml_file = tmp_path / "tgmdr.xml"
    xml_file.write_bytes(_make_minimal_xml())
    return xml_file


def test_load_ep1(minimal_xml):
    result = load_schedule1(minimal_xml)
    assert "1" in result
    ep1 = result["1"]
    assert ep1.ep_title == "Use of medical devices not to compromise health and safety"
    assert "Essential Principle 1" in ep1.citation
    assert "Schedule 1" in ep1.citation
    assert "Therapeutic Goods (Medical Devices) Regulations 2002" in ep1.citation


def test_load_subclause(minimal_xml):
    result = load_schedule1(minimal_xml)
    assert "7.1" in result
    ep71 = result["7.1"]
    assert ep71.ep_number == "7.1"
    assert "Materials must not be toxic" in ep71.text


def test_load_alphanumeric_ep(minimal_xml):
    result = load_schedule1(minimal_xml)
    assert "13A" in result, f"13A not found in {list(result.keys())}"
    ep13a = result["13A"]
    assert ep13a.ep_title == "Patient implant card"
    assert "13A" in ep13a.citation


def test_load_missing_schedule_raises(tmp_path):
    root = etree.Element(f"{{{AKN_NS}}}akomaNtoso", nsmap={None: AKN_NS})
    act = etree.SubElement(root, f"{{{AKN_NS}}}act", name="act")
    xml_file = tmp_path / "empty.xml"
    xml_file.write_bytes(etree.tostring(root, xml_declaration=True, encoding="UTF-8"))
    with pytest.raises(RuntimeError, match="Schedule 1 not found"):
        load_schedule1(xml_file)
