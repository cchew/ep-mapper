from __future__ import annotations
from ep_mapper.schema import DeviceMetadata

# (ep_number, applicability_basis, condition_func)
# condition_func returns True when the EP is NOT applicable
_NOT_APPLICABLE_RULES: list[tuple[str, str, object]] = [
    (
        "11",
        "Sch 1, cl 11 — applies to devices that emit radiation; device is non-radiation-emitting",
        lambda m: not m.radiation,
    ),
    (
        "12",
        "Sch 1, cl 12 — applies to active devices or software-present devices; device is passive and has no software",
        lambda m: not m.active and not m.software,
    ),
    (
        "13A",
        "Sch 1, cl 13A — applies to implantable devices only; device is not implantable",
        lambda m: not m.implantable,
    ),
    (
        "13B",
        "Sch 1, cl 13B — applies to software-present devices; device has no software",
        lambda m: not m.software,
    ),
    (
        "15",
        "Sch 1, cl 15 — applies to IVD medical devices only; device is non-IVD",
        lambda m: not m.ivd,
    ),
]


def ep_applicability_filter(
    meta: DeviceMetadata,
    ep_numbers: list[str],
) -> dict[str, tuple[str, str | None]]:
    """Return applicability for each EP number.

    Returns dict[ep_number, (applicability, applicability_basis)].
    applicability is 'applicable' or 'not_applicable'.
    applicability_basis is the legislative clause string if not_applicable, else None.
    """
    not_applicable_map = {ep: basis for ep, basis, cond in _NOT_APPLICABLE_RULES if cond(meta)}
    result: dict[str, tuple[str, str | None]] = {}
    for ep in ep_numbers:
        if ep in not_applicable_map:
            result[ep] = ("not_applicable", not_applicable_map[ep])
        else:
            result[ep] = ("applicable", None)
    return result


_CLASSIFICATION_CHECKS: list[tuple[str, object]] = [
    (
        "Class I + software-present is unusual — confirm device class before proceeding (standalone software is typically Class IIa or higher).",
        lambda m: m.device_class == "I" and m.software,
    ),
    (
        "Class I + implantable is unusual — implantable devices are typically Class IIb or III.",
        lambda m: m.device_class == "I" and m.implantable,
    ),
    (
        "Class I + radiation-emitting is unusual — radiation-emitting devices are typically Class IIa or higher.",
        lambda m: m.device_class == "I" and m.radiation,
    ),
]


def classification_warnings(meta: DeviceMetadata) -> list[str]:
    """Return non-blocking warnings for unusual device class combinations."""
    return [msg for msg, cond in _CLASSIFICATION_CHECKS if cond(meta)]
