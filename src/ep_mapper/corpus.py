from __future__ import annotations
import re
from pathlib import Path
from lxml import etree
from ep_mapper.schema import EpClause

AKN_NS = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"
AKN = f"{{{AKN_NS}}}"
_REGULATION_CITATION = "Therapeutic Goods (Medical Devices) Regulations 2002"

# Disable entity resolution and network access — the corpus path can be pointed
# at an arbitrary file via LEX_AU_CORPUS_DIR, so treat the XML as untrusted.
_XML_PARSER = etree.XMLParser(resolve_entities=False, no_network=True)


def _collect_text(el: etree._Element) -> str:
    return " ".join(t.strip() for t in el.itertext() if t.strip())


def _make_citation(ep_number: str) -> str:
    return f"Essential Principle {ep_number}, Schedule 1, {_REGULATION_CITATION}"


def load_schedule1(xml_path: Path) -> dict[str, EpClause]:
    """Load all EP clauses and sub-clauses from TG(MD)R 2002 Schedule 1 AKN XML.

    Returns dict keyed by EP number string: "1", "7.3", "13A", etc.
    """
    tree = etree.parse(str(xml_path), parser=_XML_PARSER)
    root = tree.getroot()

    schedules = root.findall(f".//{AKN}hcontainer[@name='schedule']")
    schedule_1 = next((s for s in schedules if s.get("eId") == "schedule-1"), None)
    if schedule_1 is None:
        raise RuntimeError("Schedule 1 not found in AKN XML — verify lex-au corpus ingestion")

    result: dict[str, EpClause] = {}

    for clause in schedule_1.findall(f"{AKN}hcontainer[@name='clause']"):
        num_el = clause.find(f"{AKN}num")
        heading_el = clause.find(f"{AKN}heading")
        if num_el is None:
            continue
        ep_num = (num_el.text or "").strip()
        ep_title = (heading_el.text or "").strip() if heading_el is not None else ""
        eid = clause.get("eId", "")
        text = _collect_text(clause)
        result[ep_num] = EpClause(
            ep_number=ep_num,
            ep_title=ep_title,
            text=text,
            citation=_make_citation(ep_num),
            citation_uri=f"//{eid}" if eid else "",
        )

        # Sub-clauses (e.g. 7.1–7.7, 12.1–12.13, 13.1–13.4)
        for sub in clause.findall(f"{AKN}hcontainer[@name='subclause']"):
            sub_num_el = sub.find(f"{AKN}num")
            if sub_num_el is None:
                continue
            sub_num = (sub_num_el.text or "").strip()
            # Qualify bare numbers (e.g. "1" inside EP 15) as "15.1" to avoid
            # overwriting top-level EP keys in the result dict.
            if "." not in sub_num:
                sub_num = f"{ep_num}.{sub_num}"
            sub_eid = sub.get("eId", "")
            sub_text = _collect_text(sub)
            result[sub_num] = EpClause(
                ep_number=sub_num,
                ep_title=ep_title,
                text=sub_text,
                citation=_make_citation(sub_num),
                citation_uri=f"//{sub_eid}" if sub_eid else "",
            )

    return result
