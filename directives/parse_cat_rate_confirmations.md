# Parse C.A.T. Inc. Rate Confirmations

## Goal
Parse C.A.T. Inc. Rate Confirmation PDF files into structured JSON with lanes, notes, and document metadata.

## Inputs
- PDF files in a directory (default: user-supplied input dir)
- Optional single PDF file path
- Output JSON file path

## Tool
- `execution/parse_cat_rate_confirmations.py`

## Output
- JSON file containing an array of parsed documents with:
  - date/effective period
  - customer
  - equipment
  - optional service type
  - lanes with origin, destination, miles (or FSC miles), mode, flat/rate, fund type
  - notes (raw text and parsed key/value lines)

## Steps
1. Collect the input directory or a single PDF path.
2. Run `execution/parse_cat_rate_confirmations.py` with `--input-dir` or `--input-file` and `--output-file`.
3. Review the JSON for:
   - consistent miles parsing
   - correct currency and amounts
   - notes parsing
4. If fields are missing or malformed, inspect the PDF and update parsing rules.

## Edge Cases
- Headers can vary: `Origin Destination Miles MODE Flat Fund Type`, `Origin Destination FSC Miles Line Haul Fund Type`, `Origin Stops Miles Mode Linehaul Fund Type`, `Origin Stops Miles RPM Min. Fund Type`.
- Some lines include extra text between lanes (e.g., shipper names). These are appended to `lane_notes` on the previous lane.
- Miles can be split with spaces (e.g., `9 55` => 955) or include commas (e.g., `1 ,406`).
- Amounts can be split by spaces (e.g., `$ 2 .70`).
- Notes may start on the same line as `Notes:` and continue for multiple lines.

## Example Command
```
python execution/parse_cat_rate_confirmations.py --input-dir "C:\Users\ranai\Documents\Miaro - Copie" --output-file .tmp/cat_rate_confirmations.json
```