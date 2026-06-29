"""TGA guidance sub-requirements for structured extraction EPs.

Source: TGA 'Demonstrating evidence to comply with the Essential Principles'
and 'Complying with the Essential Principles' guidance documents.
These are guidance, not legislative requirements. Labelled as such in output.
"""

TGA_GUIDANCE: dict[str, list[str]] = {
    # EP 7: Chemical, physical and biological properties
    "7": [
        "7.1 Chemical composition and biocompatibility — materials do not release harmful quantities of contaminants",
        "7.2 Risk from materials of biological origin — sourcing, processing, testing documented",
        "7.3 Toxicity, carcinogenicity, mutagenicity — characterisation and testing evidence",
        "7.4 Flammability — materials are not flammable under normal conditions of use",
        "7.5 Suitability of materials in contact with tissue, blood, or other body fluids",
        "7.6 Leachables and extractables — acceptable limits demonstrated",
        "7.7 Particulate contamination — levels within acceptable limits for intended use",
    ],
    # EP 12: Medical devices connected to or equipped with an energy source
    "12": [
        "12.1 Protection against electrical hazards — insulation, earthing, fusing",
        "12.2 Protection against mechanical hazards — moving parts, sharp edges, vibration",
        "12.3 Protection against radiation — unintended radiation output minimised",
        "12.4 Protection against thermal hazards — heat generation within safe limits",
        "12.5 Protection against biological and chemical hazards from materials",
        "12.6 Alarm systems — audible/visible alarms for hazardous conditions",
        "12.7 Safe interaction with other devices and equipment",
        "12.8 Cybersecurity and software security — protection against unauthorised access",
        "12.9 Software validation — IEC 62304 or equivalent lifecycle documentation",
        "12.10 Intended accuracy of measurement or control functions",
        "12.11 Protection against risk from connected fluids or gases",
        "12.12 Reliability of energy supply and failure modes documented",
        "12.13 EMC — electromagnetic compatibility testing (IEC 60601-1-2 or equivalent)",
    ],
    # EP 14: Clinical evidence
    "14": [
        "14.1 Clinical evidence strategy — direct clinical data or equivalence pathway identified",
        "14.2 Literature review — systematic search and critical appraisal documented",
        "14.3 Clinical investigations or clinical use data for the device or equivalent",
        "14.4 Equivalence justification — technical, biological, clinical equivalence criteria met",
        "14.5 Risk-benefit analysis — clinical benefits outweigh residual risks",
        "14.6 Post-market clinical follow-up (PMCF) plan or rationale for no PMCF",
    ],
}
