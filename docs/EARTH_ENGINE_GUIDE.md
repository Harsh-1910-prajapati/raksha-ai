# Enabling Google Earth Engine

RakshaAI ships with a demo geospatial provider so the entire product runs with
zero credentials. The Earth Engine path is a drop-in replacement.

## Current integration

- `GeoDataProvider` interface lives in `backend/app/services/geo_data.py`.
- `DemoGeoDataProvider` interpolates elevation from district catalogue values
  (labelled DEMO DATA).
- `EarthEngineProvider` queries **NASA SRTM** elevation for the scenario centre
  using the Earth Engine Python client.
- `get_geo_provider()` returns `EarthEngineProvider` only when it is enabled and
  authenticated; otherwise it returns the demo provider.

## Enable locally

1. Create a Google Cloud project and enable the **Earth Engine API**,
   then register a service account with Earth Engine access (or use application
   default credentials after `earthengine authenticate`).
2. Install the client:
   ```bash
   pip install earthengine-api
   ```
3. Configure `backend/.env`:
   ```env
   EARTH_ENGINE_ENABLED=1
   EARTH_ENGINE_PROJECT=your-cloud-project
   EARTH_ENGINE_SERVICE_ACCOUNT=svc-acct@project.iam.gserviceaccount.com
   ```
4. Restart the backend. `GET /health` will report the Earth Engine provider.

## Extension points

- Coastal proximity / flood-prone land classification can be added by sampling
  candidates such as
  - `JRC/GSW1_4/GlobalSurfaceWater` (water occurrence),
  - `projects/sat-io/open-datasets/GEEDiT/HAND` (height above nearest drainage),
  - GTOPO30/COP-DEM for elevation,
  - OSM land cover (`projects/mapbiomas-public` style layers).
- Add methods to `EarthEngineProvider` and mirror them (with demo values) on
  `DemoGeoDataProvider` so the app keeps working without credentials.