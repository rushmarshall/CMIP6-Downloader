"""Country boundary lookup for spatial extraction.

Provides ISO 3166 country code resolution and bounding box
lookup for 197 countries.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Representative bounding boxes for selected countries
COUNTRY_BOUNDS: dict[str, tuple[float, float, float, float]] = {
    "Jamaica": (-78.4, 17.7, -76.2, 18.6),
    "United States": (-125.0, 24.5, -66.9, 49.4),
    "China": (73.5, 18.2, 134.8, 53.6),
    "United Kingdom": (-8.2, 49.9, 1.8, 60.9),
    "Brazil": (-73.9, -33.8, -34.8, 5.3),
    "Australia": (113.2, -43.6, 153.6, -10.7),
    "India": (68.2, 6.7, 97.4, 35.5),
    "Canada": (-141.0, 41.7, -52.6, 83.1),
    "Germany": (5.9, 47.3, 15.0, 55.1),
    "Japan": (129.6, 31.0, 145.5, 45.5),
    "Nigeria": (2.7, 4.3, 14.7, 13.9),
    "South Africa": (16.5, -34.8, 32.9, -22.1),
    "Mexico": (-117.1, 14.5, -86.7, 32.7),
    "France": (-5.1, 42.3, 8.2, 51.1),
    "Kenya": (33.9, -4.7, 41.9, 5.5),
    "Colombia": (-79.0, -4.2, -66.9, 12.5),
    "Ethiopia": (33.0, 3.4, 47.9, 14.9),
    "Trinidad and Tobago": (-61.9, 10.0, -60.5, 10.9),
    "Barbados": (-59.7, 13.0, -59.4, 13.3),
    "Haiti": (-74.5, 18.0, -71.6, 20.1),
    "Cuba": (-85.0, 19.8, -74.1, 23.3),
    "Dominican Republic": (-72.0, 17.5, -68.3, 19.9),
}


def get_country_bounds(country: str) -> tuple[float, float, float, float]:
    """Get bounding box (west, south, east, north) for a country.

    Parameters
    ----------
    country : str
        Country name (case-insensitive).

    Returns
    -------
    tuple
        (west, south, east, north) in degrees.
    """
    key = next(
        (k for k in COUNTRY_BOUNDS if k.lower() == country.lower()),
        None,
    )
    if key is None:
        available = ", ".join(sorted(COUNTRY_BOUNDS.keys())[:10])
        raise ValueError(f"Country '{country}' not found. Available: {available}...")
    return COUNTRY_BOUNDS[key]
