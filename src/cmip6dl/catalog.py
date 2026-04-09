"""ESGF catalog search and model registry.

Provides model discovery, variable lookup, and metadata
for CMIP6 datasets across ESGF federation nodes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

ESGF_NODES = [
    "https://esgf-node.llnl.gov/esg-search/search",
    "https://esgf-data.dkrz.de/esg-search/search",
    "https://esgf-index1.ceda.ac.uk/esg-search/search",
]

SUPPORTED_MODELS = [
    "ACCESS-CM2", "ACCESS-ESM1-5", "AWI-CM-1-1-MR", "BCC-CSM2-MR",
    "BCC-ESM1", "CAMS-CSM1-0", "CanESM5", "CanESM5-CanOE", "CESM2",
    "CESM2-WACCM", "CIESM", "CMCC-CM2-SR5", "CMCC-ESM2", "CNRM-CM6-1",
    "CNRM-CM6-1-HR", "CNRM-ESM2-1", "EC-Earth3", "EC-Earth3-Veg",
    "EC-Earth3-Veg-LR", "FGOALS-f3-L", "FGOALS-g3", "FIO-ESM-2-0",
    "GFDL-CM4", "GFDL-ESM4", "GISS-E2-1-G", "GISS-E2-1-H", "HadGEM3-GC31-LL",
    "HadGEM3-GC31-MM", "IITM-ESM", "INM-CM4-8", "INM-CM5-0", "IPSL-CM6A-LR",
    "KACE-1-0-G", "KIOST-ESM", "MCM-UA-1-0", "MIROC-ES2L", "MIROC6",
    "MPI-ESM1-2-HR", "MPI-ESM1-2-LR", "MRI-ESM2-0", "NESM3", "NorCPM1",
    "NorESM2-LM", "NorESM2-MM", "SAM0-UNICON", "TaiESM1", "UKESM1-0-LL",
    "E3SM-1-0", "E3SM-1-1", "GISS-E2-2-G", "ICON-ESM-LR", "IPSL-CM5A2-INCA",
    "MPI-ESM-1-2-HAM", "NorESM1-F", "NorESM2-MH", "SAM0-UNICON",
    "CESM2-FV2", "CESM2-WACCM-FV2", "GFDL-AM4", "CanESM5-1",
]

CMIP6_VARIABLES = {
    "tas": {"long_name": "Near-Surface Air Temperature", "units": "K"},
    "pr": {"long_name": "Precipitation", "units": "kg m-2 s-1"},
    "tasmax": {"long_name": "Daily Maximum Near-Surface Air Temperature", "units": "K"},
    "tasmin": {"long_name": "Daily Minimum Near-Surface Air Temperature", "units": "K"},
    "hurs": {"long_name": "Near-Surface Relative Humidity", "units": "%"},
    "sfcWind": {"long_name": "Near-Surface Wind Speed", "units": "m s-1"},
    "rsds": {"long_name": "Surface Downwelling Shortwave Radiation", "units": "W m-2"},
    "psl": {"long_name": "Sea Level Pressure", "units": "Pa"},
}

SCENARIOS = ["historical", "ssp126", "ssp245", "ssp370", "ssp585"]


@dataclass
class CatalogEntry:
    """A discovered CMIP6 dataset."""

    model: str
    variable: str
    scenario: str
    frequency: str
    opendap_url: str
    size_bytes: int = 0
    node: str = ""


class ESGFCatalog:
    """Search and discover CMIP6 datasets from ESGF nodes."""

    def __init__(self, nodes: list[str] | None = None) -> None:
        self.nodes = nodes or ESGF_NODES.copy()

    def search(
        self,
        variable: str,
        model: str,
        scenario: str,
        frequency: str = "mon",
    ) -> list[CatalogEntry]:
        """Search for CMIP6 datasets matching criteria."""
        if model not in SUPPORTED_MODELS:
            logger.warning("Model %s not in supported list", model)
        if variable not in CMIP6_VARIABLES:
            logger.warning("Variable %s not in common variables", variable)

        logger.info("Searching ESGF for %s/%s/%s/%s", model, variable, scenario, frequency)

        # Construct synthetic catalog entries for demonstration
        entries = []
        for node in self.nodes:
            entries.append(CatalogEntry(
                model=model,
                variable=variable,
                scenario=scenario,
                frequency=frequency,
                opendap_url=f"{node.replace('/search', '')}/thredds/dodsC/cmip6/{model}/{scenario}/{variable}.nc",
                node=node.split("//")[1].split("/")[0],
            ))

        return entries
