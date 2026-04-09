"""Tests for bias correction."""
import numpy as np
from cmip6dl.processing.bias import quantile_mapping, delta_change


def test_quantile_mapping():
    rng = np.random.default_rng(42)
    hist = rng.normal(20, 3, 1000)
    future = rng.normal(22, 3, 1000)
    obs = rng.normal(20, 2, 1000)
    corrected = quantile_mapping(hist, future, obs)
    assert corrected.shape == future.shape


def test_delta_change_additive():
    hist = np.array([10.0, 11.0, 12.0])
    future = np.array([12.0, 13.0, 14.0])
    obs = np.array([9.0, 10.0, 11.0])
    result = delta_change(hist, future, obs, method="additive")
    assert result.mean() > obs.mean()
