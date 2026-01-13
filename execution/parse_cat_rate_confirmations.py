import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

CURRENCY_RE = re.compile(r"\b(USD|CAD)\b", re.IGNORECASE)
HEADER_RE = re.compile(r"\bOrigin\b.*\bMiles\b", re.IGNORECASE)
LOCATION_RE = re.compile(r"^(?P<origin>.+?,\s*[A-Z]{2})\s+(?P<destination>.+?,\s*[A-Z]{2})\s+(?P<rest>.+)$")
AMOUNT_RE = re.compile(r"\$\s*[\d,\.\s]+")


def extract_text(pdf_path: Path) -> str:
    try:
        import pdfplumber  # type: ignore
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        from PyPDF2 import PdfReader  # type: ignore
        reader = PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_header(line: str) -> dict:
    lower = line.lower()
    miles_label = "FSC Miles" if "fsc" in lower else "Miles"
    has_mode = "mode" in lower
    has_rpm = "rpm" in lower
    has_min = "min" in lower

    if "line haul" in lower or "linehaul" in lower:
        flat_label = "Linehaul"
    elif "flat" in lower:
        flat_label = "Flat"
    elif "min" in lower:
        flat_label = "Min"
    elif "rate" in lower:
        flat_label = "Rate"
    else:
        flat_label = "Flat"

    return {
        "miles_label": miles_label,
        "has_mode": has_mode,
        "has_rpm": has_rpm,
        "has_min": has_min,
        "flat_label": flat_label,
    }


def normalize_number(text: str) -> str:
    compact = text.replace("$", "").replace(" ", "").replace(",", "")
    return compact


def parse_amounts(text: str) -> list:
    amounts = []
    for match in AMOUNT_RE.findall(text):
        compact = normalize_number(match)
        if not compact:
            continue
        try:
            amounts.append(float(compact))
        except ValueError:
            continue
    return amounts


def parse_miles(rest_before_money: str, mode: str | None) -> int | None:
    cleaned = rest_before_money.replace("-", " ").strip()
    if not cleaned:
        return None

    tokens = cleaned.split()
    if mode and tokens:
        tokens = tokens[:-1]

    numeric_tokens = [t for t in tokens if re.search(r"\d", t)]
    if not numeric_tokens:
        return None

    joined = "".join(numeric_tokens)
    digits = re.sub(r"\D", "", joined)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def parse_lane(line: str, header: dict) -> dict | None:
    currency_match = CURRENCY_RE.search(line)
    if not currency_match:
        return None

    location_match = LOCATION_RE.match(line)
    if not location_match:
        return None

    origin = location_match.group("origin").strip()
    destination = location_match.group("destination").strip()
    rest = location_match.group("rest").strip()

    mode = None
    rest_before_money = rest.split("$")[0] if "$" in rest else rest
    if header.get("has_mode"):
        tokens = rest_before_money.split()
        if tokens:
            last = tokens[-1]
            if re.search(r"[A-Za-z]", last) and not re.search(r"\d", last):
                mode = last

    miles = parse_miles(rest_before_money, mode)
    amounts = parse_amounts(rest)

    rpm = None
    min_amount = None
    flat = None

    if header.get("has_rpm") and header.get("has_min"):
        if len(amounts) >= 2:
            rpm = amounts[0]
            min_amount = amounts[1]
            flat = min_amount
        elif len(amounts) == 1:
            flat = amounts[0]
    else:
        if amounts:
            flat = amounts[0]

    return {
        "origin": origin,
        "destination": destination,
        "miles": miles,
        "miles_label": header.get("miles_label"),
        "mode": mode,
        "flat": flat,
        "flat_label": header.get("flat_label"),
        "rpm": rpm,
        "min": min_amount,
        "fund_type": currency_match.group(1).upper(),
        "raw_line": line,
    }


def parse_notes(lines: list[str]) -> tuple[str, dict]:
    cleaned_lines = []
    for line in lines:
        if not line:
            continue
        cleaned_lines.append(line.strip())

    raw = "\n".join(cleaned_lines)
    parsed = {"items": [], "lines": []}

    for line in cleaned_lines:
        if not line:
            continue
        if line.lower().startswith("notes"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                line = parts[1].strip()
                if not line:
                    continue
        if ":" in line:
            key, value = line.split(":", 1)
            parsed["items"].append({"key": key.strip(), "value": value.strip()})
        else:
            parsed["lines"].append(line)

    return raw, parsed


def parse_document(pdf_path: Path) -> dict:
    text = extract_text(pdf_path)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    data = {
        "file_name": pdf_path.name,
        "date": None,
        "customer": None,
        "equipment": None,
        "service_type": None,
        "lanes": [],
        "notes_raw": "",
        "notes_parsed": {"items": [], "lines": []},
    }

    for line in lines:
        if data["date"] is None:
            date_match = re.search(r"\bDate\s*:\s*(.+)$", line, re.IGNORECASE)
            if not date_match:
                date_match = re.search(r"Effective\s+period\s*:\s*(.+)$", line, re.IGNORECASE)
            if date_match:
                data["date"] = date_match.group(1).strip()
                continue
        if data["customer"] is None:
            cust_match = re.search(r"Customer\s*:\s*(.+)$", line, re.IGNORECASE)
            if cust_match:
                data["customer"] = cust_match.group(1).strip()
                continue
        if data["equipment"] is None:
            equip_match = re.search(r"Equipment\s*:\s*(.+)$", line, re.IGNORECASE)
            if equip_match:
                data["equipment"] = equip_match.group(1).strip()
                continue
        if data["service_type"] is None:
            service_match = re.search(r"Service\s*type\s*:\s*(.+)$", line, re.IGNORECASE)
            if service_match:
                data["service_type"] = service_match.group(1).strip()

    header = {
        "miles_label": "Miles",
        "has_mode": False,
        "has_rpm": False,
        "has_min": False,
        "flat_label": "Flat",
    }

    in_table = False
    last_lane = None
    notes_start_index = None

    for idx, line in enumerate(lines):
        if line.lower().startswith("notes"):
            notes_start_index = idx
            break

        if HEADER_RE.search(line) and "origin" in line.lower():
            header = parse_header(line)
            in_table = True
            continue

        if not in_table:
            continue

        lane = parse_lane(line, header)
        if lane:
            data["lanes"].append(lane)
            last_lane = lane
        else:
            if last_lane is not None:
                last_lane.setdefault("lane_notes", []).append(line)

    if notes_start_index is not None:
        notes_raw, notes_parsed = parse_notes(lines[notes_start_index:])
        data["notes_raw"] = notes_raw
        data["notes_parsed"] = notes_parsed

    return data


def collect_pdfs(input_dir: Path) -> list[Path]:
    return sorted([p for p in input_dir.iterdir() if p.suffix.lower() == ".pdf"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse C.A.T. Inc. Rate Confirmation PDFs into JSON.")
    parser.add_argument("--input-dir", type=Path, help="Directory containing PDF files")
    parser.add_argument("--input-file", type=Path, help="Single PDF file to parse")
    parser.add_argument("--output-file", type=Path, default=Path(".tmp/cat_rate_confirmations.json"))

    args = parser.parse_args()

    pdf_files: list[Path] = []
    if args.input_file:
        pdf_files = [args.input_file]
    elif args.input_dir:
        pdf_files = collect_pdfs(args.input_dir)
    else:
        raise SystemExit("Provide --input-dir or --input-file")

    documents = [parse_document(pdf_path) for pdf_path in pdf_files]

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": str(args.input_dir) if args.input_dir else str(args.input_file),
        "parsed_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "documents": documents,
    }

    with args.output_file.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    print(f"Wrote {len(documents)} documents to {args.output_file}")


if __name__ == "__main__":
    main()