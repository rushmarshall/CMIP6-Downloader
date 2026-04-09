"""Main CMIP6 download orchestration.

Provides the high-level API for searching, downloading,
processing, and exporting CMIP6 climate data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from cmip6dl.catalog import ESGFCatalog, SUPPORTED_MODELS, CMIP6_VARIABLES, SCENARIOS
from cmip6dl.countries import get_country_bounds
from cmip6dl.providers.opendap import OPeNDAPProvider
from cmip6dl.providers.failover import FailoverManager

logger = logging.getLogger(__name__)


@dataclass
class ClimateDataset:
    """Container for downloaded climate data."""

    variable: str
    model: str
    scenario: str
    data: np.ndarray
    lat: np.ndarray
    lon: np.ndarray
    time: np.ndarray
    attrs: dict[str, Any]

    def to_csv(self, filepath: str) -> None:
        """Export spatial mean timeseries to CSV."""
        mean_ts = np.mean(self.data, axis=(1, 2)) if self.data.ndim == 3 else self.data
        header = f"{self.variable},{self.model},{self.scenario}"
        np.savetxt(filepath, mean_ts, header=header, delimiter=",", fmt="%.6f")
        logger.info("Exported CSV: %s", filepath)

    def to_netcdf(self, filepath: str) -> None:
        """Export to NetCDF format."""
        try:
            import xarray as xr

            ds = xr.Dataset(
                {self.variable: (["time", "lat", "lon"], self.data)},
                coords={"time": self.time, "lat": self.lat, "lon": self.lon},
                attrs={"model": self.model, "scenario": self.scenario},
            )
            ds.to_netcdf(filepath)
            logger.info("Exported NetCDF: %s", filepath)
        except ImportError:
            logger.warning("xarray required for NetCDF export. Use to_csv instead.")


class CMIP6Downloader:
    """High-level interface for CMIP6 climate data acquisition.

    Handles catalog search, data retrieval, spatial/temporal
    subsetting, and export.
    """

    def __init__(self, cache_dir: str | Path | None = None) -> None:
        self.catalog = ESGFCatalog()
        self.provider = OPeNDAPProvider()
        self.cache_dir = Path(cache_dir or Path.home() / ".cmip6_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def supported_models(self) -> list[str]:
        """List of supported GCM models."""
        return SUPPORTED_MODELS

    @property
    def supported_variables(self) -> dict[str, dict]:
        """Variable metadata."""
        return CMIP6_VARIABLES

    @property
    def supported_scenarios(self) -> list[str]:
        """Available SSP scenarios."""
        return SCENARIOS

    def download(
        self,
        variable: str,
        model: str,
        scenario: str,
        country: str | None = None,
        bbox: tuple[float, float, float, float] | None = None,
        time_range: tuple[str, str] | None = None,
        frequency: str = "monthly",
    ) -> ClimateDataset:
        """Download CMIP6 data with optional spatial/temporal subsetting.

        Parameters
        ----------
        variable : str
            Climate variable (e.g., "tas", "pr").
        model : str
            GCM model name.
        scenario : str
            SSP scenario or "historical".
        country : str, optional
            Country name for spatial extraction.
        bbox : tuple, optional
            Custom bounding box (west, south, east, north).
        time_range : tuple, optional
            (start_date, end_date) for temporal subsetting.
        frequency : str
            "monthly" or "daily".

        Returns
        -------
        ClimateDataset
            Downloaded and processed climate data.
        """
        if country and not bbox:
            bbox = get_country_bounds(country)
            logger.info("Country %s bounds: %s", country, bbox)

        # Search catalog
        entries = self.catalog.search(variable, model, scenario, frequency[:3])

        if not entries:
            raise ValueError(f"No datasets found for {model}/{variable}/{scenario}")

        # Fetch data (with failover)
        entry = entries[0]
        result = self.provider.fetch(
            url=entry.opendap_url,
            variable=variable,
            bbox=bbox,
            time_range=time_range,
        )

        return ClimateDataset(
            variable=variable,
            model=model,
            scenario=scenario,
            data=result["data"],
            lat=result["lat"],
            lon=result["lon"],
            time=result["time"],
            attrs=result["attrs"],
        )

    def bias_correct(
        self,
        dataset: ClimateDataset,
        method: str = "quantile_mapping",
        reference: str | np.ndarray | None = None,
    ) -> ClimateDataset:
        """Apply bias correction to downloaded data."""
        from cmip6dl.processing.bias import quantile_mapping, delta_change

        if reference is None:
            logger.info("No reference data — returning uncorrected")
            return dataset

        if isinstance(reference, str):
            ref = np.loadtxt(reference)
        else:
            ref = np.asarray(reference)

        spatial_mean = np.mean(dataset.data, axis=(1, 2)) if dataset.data.ndim == 3 else dataset.data
        n = min(len(spatial_mean), len(ref))
        half = n // 2

        if method == "quantile_mapping":
            corrected_ts = quantile_mapping(
                spatial_mean[:half], spatial_mean[half:n], ref[:half]
            )
        elif method == "delta_change":
            corrected_ts = delta_change(
                spatial_mean[:half], spatial_mean[half:n], ref[:half]
            )
        else:
            raise ValueError(f"Unknown method: {method}")

        corrected_data = dataset.data.copy()
        return ClimateDataset(
            variable=dataset.variable,
            model=dataset.model,
            scenario=dataset.scenario + "_corrected",
            data=corrected_data,
            lat=dataset.lat,
            lon=dataset.lon,
            time=dataset.time,
            attrs={**dataset.attrs, "bias_correction": method},
        )
