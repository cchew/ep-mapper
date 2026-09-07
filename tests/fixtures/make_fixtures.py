#!/usr/bin/env python3
"""Generate synthetic evidence PDFs for testing."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

OUT_DIR = Path(__file__).parent

SCENARIO1_PAGES = [
    """\
TECHNICAL DOCUMENTATION — InfuPro 200 (Draft)
Device: SimpStrap Pro | Class I passive bandage | Non-IVD | Non-active | No software

SECTION 1 — SAFETY AND INTENDED PURPOSE
The SimpStrap Pro is a Class I passive wound dressing intended for management of minor
skin wounds in community settings. The device has been designed to ensure that it does
not compromise the health and safety of patients, users, or third parties when used
as intended. A risk management process has been conducted in accordance with ISO 14971:2019.
All identified risks have been reduced to acceptable levels.
""",
    """\
SECTION 2 — DESIGN AND CONSTRUCTION
The device consists of woven cotton gauze and medical grade adhesive. All materials
have been selected for their established history of use in wound care. Biocompatibility
has been assessed with reference to ISO 10993-1:2018. No materials of biological origin
are used. The device is not flammable under normal conditions of use.

SECTION 3 — INFORMATION PROVIDED WITH THE DEVICE
The device is supplied with labelling compliant with the requirements of Schedule 1
of the Therapeutic Goods (Medical Devices) Regulations 2002. The label includes:
- Device name and intended purpose
- Manufacturer name and address
- Batch/lot number and expiry date
- Instructions for use
- Single use only indication
- Storage conditions
All information is provided in English and uses the standard ISO 15223-1 symbols.
""",
    """\
SECTION 4 — MANUFACTURING AND QUALITY
Manufacturing is conducted under ISO 13485:2016 certified quality management system.
Shelf life has been validated to 36 months under specified storage conditions.
Transport and storage studies demonstrate the device is not adversely affected
by transport or storage conditions within the validated range.

SECTION 5 — BENEFIT-RISK ANALYSIS
Clinical benefits of wound management with SimpStrap Pro outweigh any residual
undesirable effects. No serious adverse events are anticipated for a Class I
passive wound dressing used as intended.
""",
]

SCENARIO2_PAGES = [
    """\
TECHNICAL DOCUMENTATION — VenaFlow 3000
Device: VenaFlow 3000 | Class IIa active infusion pump | Non-IVD | Active | Software present

SECTION 1 — SAFETY AND INTENDED PURPOSE
The VenaFlow 3000 is an electronic infusion pump for controlled intravenous delivery
of medication in hospital settings. A comprehensive risk management file has been
prepared per ISO 14971:2019. Hazard analysis, FMEA, and risk controls are documented.
All residual risks have been assessed as acceptable given the clinical benefits.
The device has been designed and manufactured to ensure that when used by trained
clinical staff for its intended purpose, risks to patients are minimised.
""",
    """\
SECTION 2 — ELECTRICAL SAFETY AND SOFTWARE
Electrical safety testing has been conducted in accordance with IEC 60601-1:2018.
The device operates on mains power (240V AC) with a medical grade power supply.
Insulation, earthing, and fusing meet the requirements of IEC 60601-1. EMC testing
was conducted per IEC 60601-1-2:2014+AMD1:2020. No electromagnetic interference
was identified that would affect device function.

Software development followed IEC 62304:2006 medical software lifecycle process.
Software validation testing is documented in the software verification and validation report.
The software version is identified as VF3000-SW-v2.1.4 and is indicated on the device label.
""",
    """\
SECTION 3 — MICROBIAL CONTAMINATION
The VenaFlow 3000 fluid path components are sterile as supplied. Sterilisation
is by ethylene oxide per ISO 11135. Sterility is maintained until the expiry date
under specified storage conditions. Biocompatibility of fluid-path materials
was assessed per ISO 10993-1:2018 with biological evaluation studies conducted.

SECTION 4 — CLINICAL EVIDENCE
Clinical use data for the VenaFlow 3000 was compiled from peer-reviewed literature
on equivalent infusion pump devices. Literature search conducted per MEDLINE, EMBASE
(2010-2025). No serious adverse events attributable to device malfunction were
identified. Clinical evaluation report (CER-VF3000-v1.0) is included in the
technical documentation.

NOTE: No UDI documentation has been prepared. UDI compliance plan is pending.
""",
]

SCENARIO3_PAGES = [
    """\
TECHNICAL DOCUMENTATION — CerebroStim X1
Device: CerebroStim X1 | Class IIb active implantable neural stimulator | Non-IVD | Active | Software present

SECTION 1 — SAFETY AND GENERAL PRINCIPLES
The CerebroStim X1 is an implantable neurostimulator for management of treatment-resistant
epilepsy. Risk management per ISO 14971:2019 covers all phases of device lifecycle.
Benefit-risk conclusion: clinical benefits of seizure reduction outweigh risks of
surgical implantation and device malfunction for eligible patients.

SECTION 2 — BIOCOMPATIBILITY (EP 7 — PARTIAL)
Materials have been characterised per ISO 10993-1:2018.
7.1 Chemical composition: titanium housing, platinum-iridium electrodes, medical grade epoxy encapsulant.
7.2 No materials of biological origin are used.
7.3 Cytotoxicity and genotoxicity testing: negative for ISO 10993-5 and ISO 10993-3.
7.4 Device is not flammable.
7.5 Materials in contact with tissue: titanium and platinum-iridium have established
    biocompatibility profiles in chronic implant use.
NOTE: Leachable and particulate contamination assessments (7.6, 7.7) are in progress
and are not available in this version of the technical documentation.
""",
    """\
SECTION 3 — ELECTRICAL SAFETY AND SOFTWARE (EP 12 — PARTIAL)
IEC 60601-1:2018 testing complete for electrical safety (12.1).
Mechanical safety testing per IEC 60601-1 complete (12.2).
EMC testing per IEC 60601-1-2 complete (12.13).
Software: IEC 62304 Class C software lifecycle documentation complete (12.9).
Software version V1.2.0 is indicated on device label and patient documentation (EP 13B satisfied).

NOTE: Cybersecurity assessment (12.8) was initiated but penetration testing is
not yet complete. Cybersecurity documentation is in draft.
NOTE: Requirements for 12.3-12.7, 12.10-12.12 testing are in progress.

SECTION 4 — PATIENT IMPLANT CARD (EP 13A)
A patient implant card is provided with each device in accordance with Schedule 1
clause 13A. The card includes: device name, model number, serial number, implant date
field, surgeon field, implant site, and MRI conditional status.

SECTION 5 — INFORMATION LABELLING (EP 13)
Labelling complies with Schedule 1 clause 13 requirements including device identification,
manufacturer details, sterilisation indicator, single-use designation, and instructions.
""",
    """\
SECTION 6 — CLINICAL EVIDENCE (EP 14)
Clinical evidence strategy: direct clinical data from investigational device study.
Literature review (MEDLINE, EMBASE, Cochrane, 2000-2025): 24 relevant studies identified.
Clinical investigation: CEREBROSTIM-AU-001 study (n=45, 12-month follow-up) demonstrates
mean seizure reduction of 58% vs baseline (p<0.001). No serious device-related
adverse events in the study cohort.
Post-market clinical follow-up plan: Annual registry data collection from implanting
centres. PMCF protocol approved by ethics committee.

SECTION 7 — UDI AND TRACEABILITY
UDI assignment: in progress. CerebroStim X1 is a Class IIb device; UDI compliance
required by 1 July 2027. UDI system selection completed (GS1 GTIN). Submission
to GUDID pending. Current documentation does not yet include UDI-DI or UDI-PI.
""",
]


def _write_pdf(path: Path, pages: list[str]) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    for page_text in pages:
        y = height - 60
        for line in page_text.split("\n"):
            if y < 60:
                c.showPage()
                y = height - 60
            c.setFont("Helvetica", 9)
            c.drawString(40, y, line)
            y -= 14
        c.showPage()
    c.save()


if __name__ == "__main__":
    _write_pdf(OUT_DIR / "scenario1_class_i.pdf", SCENARIO1_PAGES)
    _write_pdf(OUT_DIR / "scenario2_class_iia.pdf", SCENARIO2_PAGES)
    _write_pdf(OUT_DIR / "scenario3_class_iib.pdf", SCENARIO3_PAGES)
    print("Fixtures generated.")
