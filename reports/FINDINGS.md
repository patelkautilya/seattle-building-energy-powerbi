# Findings | Seattle Building Energy Benchmarking

**Scope.** City of Seattle building-energy benchmarking records for calendar years 2023–2025, extracted 3 November 2026. Each row is a building-year, not a unique building. The source covers multifamily and non-residential properties generally above 20,000 square feet; it is not a census of every Seattle building. [City dataset](https://data.seattle.gov/Built-Environment/Building-Energy-Benchmarking-Data-2015-Present/teqw-tu6e).

## What the data shows

1. **The median reported site EUI is lower in 2025.** Among compliant records with positive EUI, the median was **36.2 kBtu/sq ft in 2023**, **35.1 in 2024**, and **34.6 in 2025**. These are cross-sectional medians; the included buildings can change by year.
2. **The matched-building comparison points in the same direction, but more modestly.** Of 3,562 buildings appearing in both 2024 and 2025, 3,190 were compliant and had positive site EUI in both years. The median building-level difference (2025 minus 2024) was **−0.5 kBtu/sq ft**; **59.72%** had a lower reported EUI in 2025. Weather, tenant mix, operations, reporting revisions, and other factors can affect this difference.
3. **Building type changes the benchmark.** In 2025, the median reported site EUI was **29.25** for low-rise multifamily records (n=1,000), **43.4** for non-residential (n=1,221), and **136.25** for hospitals (n=44). These are descriptive groups with different uses and operating hours; the values are not performance rankings.
4. **Completeness and status matter.** The extract contains **3,687**, **3,712**, and **3,610** building-year records for 2023, 2024, and 2025. The corresponding compliant counts are **3,544**, **3,575**, and **3,342**. The lower 2025 compliant share (92.58% of records versus 96.31% in 2024) limits a simple year-to-year interpretation of the median.

## Definitions and caveats

- **Site EUI** is annual on-site energy use divided by gross floor area, in kBtu per square foot. The report uses the source's unadjusted `SiteEUI(kBtu/sf)` field. It is not weather-normalized EUI.
- **Median site EUI** includes only records marked `Compliant` with a nonmissing, positive reported EUI. The report must apply that filter for its KPI and comparison charts. Values above 1,000 are flagged in the CSV (3, 4, and 4 compliant records by year) but retained; medians are robust to these extremes. Do not calculate a simple average without additional data-quality review.
- **GHG intensity** is kilograms CO₂e per square foot. Its median is calculated separately among compliant records with a nonmissing value. It should not be summed. [Seattle's benchmarking field definitions](https://data.seattle.gov/Built-Environment/Building-Energy-Benchmarking-Data-2015-Present/teqw-tu6e) and [City guidance](https://www.seattle.gov/environment/climate-change/buildings-and-energy/energy-benchmarking/about-benchmarking) describe the reporting context.
- **ENERGY STAR Score** is available for only a subset of records. Its median should not be interpreted as representative of all building types.
- **Compliance status** reports whether a property met benchmarking requirements for that year as of the enforcement grace period. It is not an energy-efficiency grade.
- The data is owner reported and can be revised. No causal claim is made about any policy, retrofit, or management action.

The calculations are reproduced in [`../scripts/analyze.py`](../scripts/analyze.py) and [`../analysis/summary.json`](../analysis/summary.json).
