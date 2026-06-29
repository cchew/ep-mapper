# EP Mapper

A command-line tool that maps manufacturer evidence documents against the Australian Therapeutic Goods (Medical Devices) Regulations 2002 (TG(MD)R 2002) Schedule 1 Essential Principles (EPs).

Given a PDF of technical documentation and device metadata, EP Mapper:

- Loads the 18 Essential Principles from a structured AKN XML corpus (built from the current regulation text)
- Filters applicable EPs based on device class, IVD status, and device characteristics
- Calls an LLM (Claude) to assess each EP against the evidence document
- Verifies quoted passages exist verbatim in the source PDF
- Outputs a structured gap matrix to the terminal

**Regulation pin:** Schedule 1, TG(MD)R 2002, C70 (F2026C00240, 21 Mar 2026)

> **Disclaimer:** This tool produces a documentation gap analysis only. It does not assess evidence adequacy, constitute a regulatory determination, or replace professional review before TGA submission.

---

## Prerequisites

### Python

Python 3.12 or later.

### Anthropic API key

Get a key from [console.anthropic.com](https://console.anthropic.com). Analysis runs 13–18 sequential LLM calls per document (one per applicable EP). At current pricing, a typical Class IIa device analysis costs approximately USD $0.10–0.30.

### lex-au corpus

EP Mapper reads the TG(MD)R 2002 Schedule 1 from an AKN XML file built by [lex-au](https://github.com/cchew/lex-au). You must build this corpus before using EP Mapper.

```bash
pip install lex-au
lexau build --type regulation "Therapeutic Goods (Medical Devices) Regulations 2002"
```

This downloads and converts the current regulation into AKN XML and places it in `~/lex-au-corpus/xml/` by default. Set `LEX_AU_CORPUS_DIR` to point EP Mapper at your corpus directory.

---

## Installation

```bash
git clone https://github.com/cchew/ep-mapper.git
cd ep-mapper
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development (includes pytest and fixture generation):

```bash
pip install -e ".[dev]"
```

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-...          # required
ANTHROPIC_MODEL=claude-sonnet-4-6     # optional; default: claude-sonnet-4-6
LEX_AU_CORPUS_DIR=/path/to/corpus     # optional; default: corpus/
```

`.env` is loaded automatically when `ep-mapper` (or `python main.py`) is run from the directory containing the file.

---

## Usage

```bash
ep-mapper \
  --pdf path/to/technical-documentation.pdf \
  --device-name "InfuPro 200" \
  --intended-purpose "IV medication delivery in hospital settings" \
  --device-class IIa \
  --ivd false \
  --active true \
  --implantable false \
  --radiation false \
  --software true
```

The tool prints a disclaimer and requires you to type `acknowledge` before analysis begins.

### Flags

| Flag | Required | Values | Default |
|------|----------|--------|---------|
| `--pdf` | Yes | Path to evidence PDF | — |
| `--device-name` | Yes* | String | — |
| `--intended-purpose` | No | String | `""` |
| `--device-class` | No | `I`, `IIa`, `IIb`, `III` | `I` |
| `--ivd` | No | `true` / `false` | `false` |
| `--active` | No | `true` / `false` | `false` |
| `--implantable` | No | `true` / `false` | `false` |
| `--radiation` | No | `true` / `false` | `false` |
| `--software` | No | `true` / `false` | `false` |
| `--interactive` | No | Flag | — |

*Not required when `--interactive` is used.

### Interactive mode

```bash
ep-mapper --pdf path/to/evidence.pdf --interactive
```

Prompts for device metadata at the terminal.

### Applicability filtering

EPs are automatically marked NOT APPLICABLE based on device metadata:

| EP | Condition |
|----|-----------|
| 11 | `--radiation false` |
| 12 | `--active false` and `--software false` |
| 13A | `--implantable false` |
| 13B | `--software false` |
| 15 | `--ivd false` |

### UDI compliance deadlines (EP 13C)

| Class | Deadline |
|-------|----------|
| III | 1 July 2026 |
| IIb | 1 July 2027 |
| IIa | 1 July 2028 |
| I | TBA |

---

## Running tests

```bash
pytest
```

Integration tests require the lex-au corpus at `LEX_AU_CORPUS_DIR`. They skip gracefully if absent:

```
SKIPPED tests/test_integration.py::... — TG(MD)R 2002 XML not found — run lex-au build first
```

---

## Known limitations

- **No OCR:** `pdfplumber` extracts text-layer PDFs only. Scanned images return empty pages, producing misleading all-gap results.
- **Single PDF input:** Merge fragmented technical files before analysis.
- **stdout only:** No `--output` flag; pipe to a file if needed (`ep-mapper ... > report.txt`).
- **No path confinement:** The `--pdf` argument and `LEX_AU_CORPUS_DIR` are not restricted to a safe directory. This is a local CLI tool; do not wrap it in a server without adding path validation.
- **Token cost:** No pre-flight estimate or confirmation before issuing LLM calls. Each run for a Class IIb+ device makes up to 18 API calls.

---

## License

MIT. See [LICENSE](LICENSE).
