"""Validate and summarize the City of Seattle building-year extract."""

from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
(ROOT / "analysis").mkdir(exist_ok=True)


def number(value: str) -> float | None:
    try:
        return float(value) if value else None
    except ValueError:
        return None


def median(values: list[float]) -> float | None:
    return round(statistics.median(values), 2) if values else None


def main() -> None:
    with (DATA / "benchmark_raw_fields.csv").open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    meta = json.loads((DATA / "extract_metadata.json").read_text(encoding="utf-8"))
    assert len(rows) == meta["row_count"] == sum(meta["source_counts"].values())
    assert len({(r["datayear"], r["osebuildingid"]) for r in rows}) == len(rows)

    output = []
    for r in rows:
        eui = number(r["siteeui_kbtu_sf"])
        ghg = number(r["ghgemissionsintensity"])
        score = number(r["energystarscore"])
        output.append({
            "Building ID": r["osebuildingid"],
            "Year": int(r["datayear"]),
            "Building Type": r["buildingtype"] or "Not recorded",
            "Neighborhood": r["neighborhood"] or "Not recorded",
            "ZIP": r["zipcode"] or "Not recorded",
            "Year Built": r["yearbuilt"],
            "Gross Floor Area (sq ft)": r["propertygfatotal"],
            "Compliance Status": r["compliancestatus"] or "Not recorded",
            "Site EUI (kBtu/sq ft)": eui if eui is not None and eui > 0 else "",
            "GHG Intensity (kg CO2e/sq ft)": ghg if ghg is not None and ghg >= 0 else "",
            "ENERGY STAR Score": score if score is not None and 1 <= score <= 100 else "",
            "Site EUI over 1,000": "Yes" if eui is not None and eui > 1000 else "No",
        })

    with (DATA / "seattle_benchmarking_2023_2025.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)

    by_year = {}
    by_type = {}
    for year in (2023, 2024, 2025):
        group = [r for r in output if r["Year"] == year]
        compliant = [r for r in group if r["Compliance Status"] == "Compliant"]
        euis = [float(r["Site EUI (kBtu/sq ft)"]) for r in compliant if r["Site EUI (kBtu/sq ft)"] != ""]
        ghgs = [float(r["GHG Intensity (kg CO2e/sq ft)"]) for r in compliant if r["GHG Intensity (kg CO2e/sq ft)"] != ""]
        scores = [float(r["ENERGY STAR Score"]) for r in compliant if r["ENERGY STAR Score"] != ""]
        by_year[str(year)] = {
            "building_year_records": len(group),
            "compliant_records": len(compliant),
            "not_compliant_records": len(group) - len(compliant),
            "compliance_record_rate_pct": round(100 * len(compliant) / len(group), 2),
            "compliant_with_site_eui": len(euis),
            "median_site_eui_kbtu_per_sqft": median(euis),
            "median_ghg_intensity_kgco2e_per_sqft": median(ghgs),
            "median_energy_star_score": median(scores),
            "eui_over_1000_count": sum(x > 1000 for x in euis),
        }
        types = defaultdict(list)
        for r in compliant:
            if r["Site EUI (kBtu/sq ft)"] != "":
                types[r["Building Type"]].append(float(r["Site EUI (kBtu/sq ft)"]))
        by_type[str(year)] = {k: {"records": len(v), "median_site_eui": median(v)} for k, v in sorted(types.items())}

    id_year = {(r["Building ID"], r["Year"]): r for r in output}
    paired = [(id_year[(bid, 2024)], r) for (bid, year), r in id_year.items() if year == 2025 and (bid, 2024) in id_year]
    paired_valid = [(a, b) for a, b in paired if a["Compliance Status"] == b["Compliance Status"] == "Compliant" and a["Site EUI (kBtu/sq ft)"] != "" and b["Site EUI (kBtu/sq ft)"] != ""]
    paired_change = [float(b["Site EUI (kBtu/sq ft)"]) - float(a["Site EUI (kBtu/sq ft)"]) for a, b in paired_valid]
    summary = {
        "scope": "City of Seattle benchmarking building-year records, 2023-2025",
        "unit_of_analysis": "one building-year record",
        "record_counts_by_year": dict(Counter(str(r["Year"]) for r in output)),
        "by_year": by_year,
        "by_building_type": by_type,
        "matched_2024_2025": {
            "all_paired_buildings": len(paired),
            "paired_compliant_with_positive_site_eui_both_years": len(paired_valid),
            "median_building_level_eui_change_kbtu_per_sqft": median(paired_change),
            "share_with_lower_site_eui_pct": round(100 * sum(x < 0 for x in paired_change) / len(paired_change), 2),
        },
        "notes": [
            "Medians use compliant records with a nonmissing, positive reported site EUI; extreme reported values remain in the extract and are flagged, not silently removed.",
            "The matched-cohort statistic compares the same building IDs in 2024 and 2025; it does not establish the cause of a change.",
            "Reported emissions intensity is a separate metric; no sum of its values is meaningful.",
        ],
    }
    (ROOT / "analysis" / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"by_year": by_year, "matched_2024_2025": summary["matched_2024_2025"]}, indent=2))


if __name__ == "__main__":
    main()
