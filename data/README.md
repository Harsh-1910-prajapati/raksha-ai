# Data catalogue

The `data/` folder holds small, human-editable JSON used by the demo
providers and the risk engine.

## Files

- `locations.json` — India states and coastal demo districts. Each district
  carries a representative coordinate, mean elevation (m), coastal flag,
  flood-prone classification, and population. These are approximate model
  inputs, **not official government statistics**, and are labelled DEMO DATA
  in the UI.
- `disaster_types.json` — the disaster configuration system
  (CYCLONE / FLOOD / EXTREME_RAINFALL) with default scenario parameters.

## Adding a state / district

Add an entry to `locations.json`:

```json
{
  "id": "kl",
  "name": "Kerala",
  "coastal": true,
  "districts": [
    {
      "id": "alappuzha",
      "name": "Alappuzha",
      "latitude": 9.4933,
      "longitude": 76.3287,
      "meanElevationM": 4,
      "coastal": true,
      "floodProne": "critical",
      "population": 2127789,
      "populationSqKm": 930,
      "areaSqKm": 1414
    }
  ]
}
```

No code changes are needed — `GET /api/locations/states` and the district
selector pick it up automatically.

## Upstream sources (for future real data)

- IMD / IMD-Hydro for rainfall and cyclone bulletins
- ISRO Bhuvan / Survey of India for administrative geography
- NASA SRTM / COP-DEM for elevation
- OpenStreetMap for road and facility geometry
- Census 2011 population data (via district aggregates)

Each ingested dataset must be documented with its date and licence before being
promoted beyond demo data.