#!/usr/bin/env python3
"""
Fix CSV files where the feedback_text field contains unquoted commas.

This script reads an input CSV with header:
student_id,feedback_text,category,date,rating,department,campus

If lines have more than 7 comma-separated parts, it will join the middle
parts back into the `feedback_text` field and write a properly quoted CSV.

Usage:
    python scripts/fix_csv.py data/sample_feedback.csv data/sample_feedback_fixed.csv

"""
import sys
import csv
from pathlib import Path


def fix_csv(input_path: Path, output_path: Path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1

    with input_path.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8", newline="") as fout:
        header = fin.readline().rstrip("\n")
        # Validate header
        expected_cols = ["student_id", "feedback_text", "category", "date", "rating", "department", "campus"]
        hdr_parts = [p.strip() for p in header.split(",")]
        if len(hdr_parts) < 7:
            print("Unexpected header format. Aborting.")
            print("Header:", header)
            return 1

        writer = csv.writer(fout, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(expected_cols)

        fixed = 0
        unchanged = 0
        skipped = 0

        for lineno, raw in enumerate(fin, start=2):
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split(",")
            if len(parts) == 7:
                # Good line; write as-is (but ensure proper quoting)
                writer.writerow([p for p in parts])
                unchanged += 1
            elif len(parts) > 7:
                # Reconstruct: parts[0]=student_id, parts[-5..-1]=category,date,rating,department,campus
                student_id = parts[0]
                category = parts[-5]
                date = parts[-4]
                rating = parts[-3]
                department = parts[-2]
                campus = parts[-1]
                feedback = ",".join(parts[1:-5]).strip()
                writer.writerow([student_id, feedback, category, date, rating, department, campus])
                fixed += 1
            else:
                print(f"Skipping malformed line {lineno}: expected >=7 fields, got {len(parts)}")
                skipped += 1

    print(f"Wrote fixed CSV to: {output_path}")
    print(f"Lines unchanged: {unchanged}, fixed: {fixed}, skipped: {skipped}")
    return 0


def main(argv):
    if len(argv) < 2:
        print("Usage: fix_csv.py INPUT_CSV OUTPUT_CSV")
        return 1
    input_path = Path(argv[0])
    output_path = Path(argv[1])
    return fix_csv(input_path, output_path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
