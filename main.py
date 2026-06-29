#!/usr/bin/env python3
"""EP Mapper CLI — TGA Essential Principles gap analysis tool.

Usage:
  python main.py \\
    --pdf path/to/evidence.pdf \\
    --device-name "InfuPro 200" \\
    --intended-purpose "IV medication delivery in hospital settings" \\
    --device-class IIa \\
    --ivd false \\
    --active true \\
    --implantable false \\
    --radiation false \\
    --software true

  # Interactive metadata form:
  python main.py --pdf path/to/evidence.pdf --interactive

Single PDF only. For fragmented technical files, merge relevant sections into one PDF before upload.
"""
import argparse
import glob
import os
import sys
from datetime import datetime
from pathlib import Path

from ep_mapper.metadata import parse_metadata_from_args, prompt_metadata_interactive
from ep_mapper.applicability import classification_warnings
from ep_mapper.pipeline import run_analysis
from ep_mapper.output import format_gap_matrix


def _load_env() -> None:
    env_file = Path(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def _lex_au_xml_path() -> Path:
    corpus_dir = Path(os.environ.get("LEX_AU_CORPUS_DIR", "../../lex-au/repo/corpus"))
    matches = list(glob.glob(str(corpus_dir / "xml" / "*therapeutic*medical*devices*")))
    if not matches:
        matches = list(glob.glob(str(corpus_dir / "xml" / "*therapeutic*")))
    if not matches:
        raise FileNotFoundError(
            f"TG(MD)R 2002 XML not found in {corpus_dir}/xml/. "
            "Run: cd projects/lex-au/repo && lexau build --type regulation "
            "'Therapeutic Goods (Medical Devices) Regulations 2002'"
        )
    return Path(sorted(matches)[0])


def main() -> None:
    _load_env()

    parser = argparse.ArgumentParser(description="TGA Essential Principles gap analysis")
    parser.add_argument("--pdf", required=True, help="Path to evidence PDF")
    parser.add_argument("--interactive", action="store_true", help="Interactive metadata form")
    parser.add_argument("--device-name", default="")
    parser.add_argument("--intended-purpose", default="")
    parser.add_argument("--device-class", choices=["I", "IIa", "IIb", "III"], default="I")
    parser.add_argument("--ivd", default="false")
    parser.add_argument("--active", default="false")
    parser.add_argument("--implantable", default="false")
    parser.add_argument("--radiation", default="false")
    parser.add_argument("--software", default="false")
    args = parser.parse_args()

    if args.interactive:
        meta = prompt_metadata_interactive()
    else:
        if not args.device_name:
            parser.error("--device-name is required (or use --interactive)")
        meta = parse_metadata_from_args(args)

    for warning in classification_warnings(meta):
        print(f"WARNING: {warning}", file=sys.stderr)

    print("\n" + "=" * 72)
    print("DISCLAIMER: This output is a documentation gap analysis only.")
    print("It does not assess evidence adequacy, constitute a regulatory")
    print("determination, or replace professional review before TGA submission.")
    print("=" * 72)
    ack = input("\nType 'acknowledge' to proceed: ").strip().lower()
    if ack != "acknowledge":
        print("Acknowledgment required. Exiting.")
        sys.exit(1)
    disclaimer_timestamp = datetime.now().isoformat(timespec="seconds")

    pdf_path = Path(args.pdf)
    lex_au_xml = _lex_au_xml_path()

    print(f"\nAnalysing {pdf_path.name} against TG(MD)R 2002 Schedule 1...")
    rows, pages, page_count = run_analysis(pdf_path, meta, lex_au_xml, disclaimer_timestamp)

    output = format_gap_matrix(rows, meta, pdf_path, page_count, disclaimer_timestamp)
    print(output)


if __name__ == "__main__":
    main()
