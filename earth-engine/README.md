# Earth Engine adapter

RakshaAI uses Google Earth Engine for geospatial/environmental data when
credentials are available, and a demo provider otherwise.

```text
Frontend → Backend API → GeoDataProvider
     ├── EarthEngineProvider   (NASA SRTM elevation)
     └── DemoGeoDataProvider   (deterministic demo interpolation)
```

See `docs/EARTH_ENGINE_GUIDE.md` for the step-by-step enablement guide and the
datasets we plan to add (surface water, HAND, COP-DEM, OSM land cover).