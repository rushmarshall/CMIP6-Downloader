"""Tests for CMIP6 downloader."""
from cmip6dl import CMIP6Downloader


def test_download_synthetic():
    dl = CMIP6Downloader()
    data = dl.download(
        variable="pr",
        model="GFDL-ESM4",
        scenario="ssp245",
        country="Jamaica",
    )
    assert data.variable == "pr"
    assert data.model == "GFDL-ESM4"
    assert data.data.shape[0] > 0


def test_supported_models():
    dl = CMIP6Downloader()
    assert len(dl.supported_models) >= 50


def test_country_bounds():
    from cmip6dl.countries import get_country_bounds
    bounds = get_country_bounds("Jamaica")
    assert bounds[0] < bounds[2]  # west < east
    assert bounds[1] < bounds[3]  # south < north
