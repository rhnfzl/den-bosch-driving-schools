#!/usr/bin/env python3
"""Parse the CBR CSV into research/schools.json (the canonical work-list).

Each entry carries a stable row_index (1..N over the data rows) which is the
join key used by every downstream step, so we never fuzzy-match on names.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "den_bosch_rijscholen_auto.csv")
OUT = os.path.join(ROOT, "research", "schools.json")


def to_int(value):
    value = (value or "").strip()
    return int(value) if value.isdigit() else None


def main():
    rows = []
    with open(SRC, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader, start=1):
            rows.append(
                {
                    "row_index": i,
                    "slug": f"school_{i:03d}",
                    "rijschool": row["rijschool"].strip(),
                    "plaats": row["plaats"].strip().lstrip("'"),
                    "aantal_examens": to_int(row["aantal_examens"]),
                    "first_rate": to_int(row["slagingspercentage_eerste_examens"]),
                    "all_rate": to_int(row["slagingspercentage_alle_examens"]),
                }
            )

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)

    print(f"Wrote {len(rows)} schools -> {OUT}")
    # Sanity peek
    for r in rows[:3] + rows[-2:]:
        print(f"  {r['slug']}: {r['rijschool']} ({r['plaats']}) n={r['aantal_examens']} "
              f"first={r['first_rate']} all={r['all_rate']}")


if __name__ == "__main__":
    main()
