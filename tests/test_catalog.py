"""Tests for CMIP6 catalog."""
from cmip6dl.catalog import ESGFCatalog, SUPPORTED_MODELS, CMIP6_VARIABLES


def test_model_count():
    assert len(SUPPORTED_MODELS) >= 50


def test_variable_registry():
    assert "tas" in CMIP6_VARIABLES
    assert "pr" in CMIP6_VARIABLES


def test_catalog_search():
    catalog = ESGFCatalog()
    entries = catalog.search("pr", "GFDL-ESM4", "ssp245")
    assert len(entries) > 0
    assert entries[0].model == "GFDL-ESM4"
