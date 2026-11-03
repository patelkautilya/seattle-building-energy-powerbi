"""Fetch a bounded Seattle building-energy benchmark extract from Socrata."""

from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)
RESOURCE = "https://data.seattle.gov/resource/teqw-tu6e.json"
YEARS = ("2023", "2024", "2025")
FIELDS = (
    "osebuildingid", "datayear", "buildingtype", "neighborhood", "zipcode",
    "yearbuilt", "propertygfatotal", "energystarscore", "siteeui_kbtu_sf",
    "siteenergyuse_kbtu", "electricity_kwh", "naturalgas_therms",
    "totalghgemissions", "ghgemissionsintensity", "compliancestatus", "demolished",
)


def get(params: dict[str, str]) -> list[dict[str, str]]:
    url = RESOURCE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "KautilyaPatel-portfolio/1.0"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.load(response)


def main() -> None:
    where = "datayear in('2023','2024','2025')"
    counts = get({"$select": "datayear,count(*) as n", "$where": where, "$group": "datayear"})
    source_counts = {r["datayear"]: int(r["n"]) for r in counts}
    assert set(source_counts) == set(YEARS), source_counts

    rows: list[dict[str, str]] = []
    for offset in range(0, sum(source_counts.values()), 5000):
        rows.extend(get({
            "$select": ",".join(FIELDS), "$where": where,
            "$order": "datayear,osebuildingid", "$limit": "5000", "$offset": str(offset),
        }))
    actual = Counter(r["datayear"] for r in rows)
    assert dict(actual) == source_counts, (actual, source_counts)
    keys = [(r["datayear"], r["osebuildingid"]) for r in rows]
    assert len(keys) == len(set(keys)), "Duplicate building-year keys"

    with (DATA / "benchmark_raw_fields.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    (DATA / "extract_metadata.json").write_text(json.dumps({
        "source": "https://data.seattle.gov/Built-Environment/Building-Energy-Benchmarking-Data-2015-Present/teqw-tu6e",
        "resource": RESOURCE, "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "years": YEARS, "source_counts": source_counts, "row_count": len(rows),
        "fields": FIELDS, "license": "Public Domain (as listed by City of Seattle)",
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Fetched {len(rows):,} building-year records: {dict(actual)}")
    for field in ("buildingtype", "compliancestatus", "demolished"):
        print(field, Counter(r.get(field, "<missing>") for r in rows).most_common(12))


if __name__ == "__main__":
    main()
