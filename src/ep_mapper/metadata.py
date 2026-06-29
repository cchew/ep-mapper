from __future__ import annotations
import argparse
from ep_mapper.schema import DeviceMetadata

_DEVICE_CLASSES = ("I", "IIa", "IIb", "III")


def _parse_bool(value: str) -> bool:
    return value.lower() in ("true", "yes", "1", "y")


def parse_metadata_from_args(args: argparse.Namespace) -> DeviceMetadata:
    return DeviceMetadata(
        device_name=args.device_name,
        intended_purpose=args.intended_purpose,
        device_class=args.device_class,
        ivd=_parse_bool(args.ivd),
        active=_parse_bool(args.active),
        implantable=_parse_bool(args.implantable),
        radiation=_parse_bool(args.radiation),
        software=_parse_bool(args.software),
    )


def prompt_metadata_interactive() -> DeviceMetadata:
    print("\n--- Device Metadata ---")
    device_name = input("Device name: ").strip()
    intended_purpose = input("Intended purpose: ").strip()
    print(f"Device class [{'/'.join(_DEVICE_CLASSES)}]: ", end="")
    device_class = input().strip().upper()
    while device_class not in _DEVICE_CLASSES:
        print(f"  Enter one of: {', '.join(_DEVICE_CLASSES)}: ", end="")
        device_class = input().strip().upper()

    def _ask_bool(prompt: str) -> bool:
        ans = input(f"{prompt} [y/n]: ").strip().lower()
        return ans in ("y", "yes", "1")

    ivd = _ask_bool("IVD device?")
    active = _ask_bool("Active device (uses energy source)?")
    implantable = _ask_bool("Implantable?")
    radiation = _ask_bool("Radiation-emitting?")
    software = _ask_bool("Software present?")

    return DeviceMetadata(
        device_name=device_name,
        intended_purpose=intended_purpose,
        device_class=device_class,
        ivd=ivd,
        active=active,
        implantable=implantable,
        radiation=radiation,
        software=software,
    )
