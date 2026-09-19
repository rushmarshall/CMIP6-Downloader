<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:111111,30:333333,60:666666,100:999999&height=180&section=header&text=CMIP6-Downloader&fontSize=42&fontColor=FFFFFF&animation=fadeIn&fontAlignY=36&desc=Climate%20Model%20Data%20Acquisition%20%26%20Processing%20Toolkit&descSize=14&descColor=CCCCCC&descAlignY=56"/>

<p align="center">
<img src="https://img.shields.io/badge/Python-3.9+-333333?style=flat-square&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/License-MIT-333333?style=flat-square" alt="License"/>
<img src="https://img.shields.io/badge/CMIP6-333333?style=flat-square" alt="CMIP6"/>
<img src="https://img.shields.io/badge/GCMs-61-333333?style=flat-square" alt="GCMs"/>
<img src="https://img.shields.io/badge/Countries-197-333333?style=flat-square" alt="Countries"/>
</p>

---

## Overview

**CMIP6-Downloader** is a Python toolkit for downloading, subsetting, and processing CMIP6 (Coupled Model Intercomparison Project Phase 6) climate model data. It supports OPeNDAP subsetting, multi-server failover, spatial/temporal extraction, and bias correction — covering 61 GCMs across 197 countries.

Built for climate scientists, water resources engineers, and impact modelers who need reproducible, efficient access to global climate projections.

---

## Features

- **61 GCMs Supported** — All major CMIP6 models from ESGF nodes
- **197 Country Boundaries** — Automatic spatial extraction by country or custom bbox
- **OPeNDAP Subsetting** — Server-side slicing to minimize data transfer
- **Multi-Server Failover** — Automatic retry across LLNL, DKRZ, CEDA, NCI nodes
- **Bias Correction** — Quantile mapping and delta change methods
- **Variable Support** — Temperature, precipitation, humidity, wind, radiation, pressure
- **Scenario Coverage** — SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5, historical
- **Export Formats** — NetCDF, CSV, GeoTIFF, Zarr
- **Parallel Downloads** — Concurrent retrieval with progress tracking

---

## Installation

```bash
pip install cmip6-downloader
```

Or from source:

```bash
git clone https://github.com/rushmarshall/CMIP6-Downloader.git
cd CMIP6-Downloader
pip install -e ".[dev]"
```

---

## Quick Start

```python
from cmip6dl import CMIP6Downloader

dl = CMIP6Downloader()

# Download monthly precipitation for Jamaica (SSP2-4.5, 2030-2060)
data = dl.download(
    variable="pr",
    model="GFDL-ESM4",
    scenario="ssp245",
    country="Jamaica",
    time_range=("2030-01-01", "2060-12-31"),
    frequency="monthly",
)

# Apply bias correction against observed data
corrected = dl.bias_correct(
    data,
    method="quantile_mapping",
    reference="observed_precip.nc",
)

# Export
corrected.to_netcdf("jamaica_pr_ssp245_2030-2060_corrected.nc")
corrected.to_csv("jamaica_pr_ssp245_2030-2060.csv")
```

---

## Supported Models (61 GCMs)

<details>
<summary>View full model list</summary>

| Model | Institution | Resolution |
|:------|:-----------|:-----------|
| ACCESS-CM2 | CSIRO-ARCCSS | 250 km |
| ACCESS-ESM1-5 | CSIRO | 250 km |
| BCC-CSM2-MR | BCC-CMA | 100 km |
| CanESM5 | CCCma | 500 km |
| CESM2 | NCAR | 100 km |
| CNRM-CM6-1 | CNRM-CERFACS | 250 km |
| EC-Earth3 | EC-Earth Consortium | 100 km |
| GFDL-ESM4 | NOAA-GFDL | 100 km |
| INM-CM5-0 | INM | 200 km |
| IPSL-CM6A-LR | IPSL | 250 km |
| MIROC6 | MIROC | 250 km |
| MPI-ESM1-2-HR | MPI-M | 100 km |
| MRI-ESM2-0 | MRI | 100 km |
| NorESM2-LM | NCC | 250 km |
| UKESM1-0-LL | MOHC-NERC | 250 km |
| ... | ... | ... |

*61 models total across all major modeling centers*

</details>

---

## Scenarios

| Scenario | Description | Radiative Forcing |
|:---------|:-----------|:-----------------|
| historical | Observed forcings (1850-2014) | N/A |
| ssp126 | Sustainability | 2.6 W/m2 |
| ssp245 | Middle of the road | 4.5 W/m2 |
| ssp370 | Regional rivalry | 7.0 W/m2 |
| ssp585 | Fossil-fueled development | 8.5 W/m2 |

---

## Architecture

```
cmip6dl/
├── downloader.py       # Main download orchestration
├── catalog.py          # ESGF catalog search & model registry
├── providers/          # Data source backends
│   ├── opendap.py          OPeNDAP with server-side subsetting
│   ├── http.py             Direct HTTP/HTTPS download
│   └── failover.py         Multi-server failover logic
├── processing/         # Post-processing
│   ├── spatial.py          Country extraction, regridding
│   ├── temporal.py         Aggregation, resampling
│   └── bias.py             Bias correction methods
└── countries.py        # ISO 3166 country boundary lookup
```

---

## Configuration

```yaml
providers:
  primary: "https://esgf-node.llnl.gov/esg-search"
  fallback:
    - "https://esgf-data.dkrz.de/esg-search"
    - "https://esgf-index1.ceda.ac.uk/esg-search"

download:
  n_workers: 4
  retry_attempts: 3
  timeout: 120
  chunk_size: 50_000_000

output:
  directory: "./cmip6_data"
  format: "netcdf"
```

---

## Contributing

Contributions welcome. Please open an issue to discuss proposed changes before submitting a pull request.

---

<p align="center">
<sub>Developed at Hydrosense Lab, University of Virginia</sub>
<br>
<sub>Part of the Global Hydrology and Water Resources research group</sub>
</p>

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:999999,30:666666,60:333333,100:111111&height=100&section=footer"/>
