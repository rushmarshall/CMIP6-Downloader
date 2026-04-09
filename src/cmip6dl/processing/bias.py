"""Bias correction methods for climate model output.

Implements quantile mapping and delta change bias correction
methods for post-processing GCM projections.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


def quantile_mapping(
    model_hist: np.ndarray,
    model_future: np.ndarray,
    observed: np.ndarray,
    n_quantiles: int = 100,
) -> np.ndarray:
    """Apply quantile mapping bias correction.

    Maps the CDF of model output to match the CDF of observations
    using empirical quantile-quantile transformation.

    Parameters
    ----------
    model_hist : np.ndarray
        Historical model data (calibration period).
    model_future : np.ndarray
        Future model data to correct.
    observed : np.ndarray
        Observed reference data.
    n_quantiles : int
        Number of quantile bins.

    Returns
    -------
    np.ndarray
        Bias-corrected future data.
    """
    quantiles = np.linspace(0, 1, n_quantiles + 1)
    model_quantiles = np.quantile(model_hist.flatten(), quantiles)
    obs_quantiles = np.quantile(observed.flatten(), quantiles)

    corrected = np.interp(
        model_future.flatten(),
        model_quantiles,
        obs_quantiles,
    ).reshape(model_future.shape)

    logger.info(
        "Quantile mapping applied: mean shift %.3f -> %.3f",
        float(np.mean(model_future)),
        float(np.mean(corrected)),
    )
    return corrected


def delta_change(
    model_hist: np.ndarray,
    model_future: np.ndarray,
    observed: np.ndarray,
    method: str = "additive",
) -> np.ndarray:
    """Apply delta change bias correction.

    Applies the change signal from the model (future - historical)
    to the observed data.

    Parameters
    ----------
    model_hist, model_future : np.ndarray
        Model historical and future data.
    observed : np.ndarray
        Observed reference data.
    method : str
        "additive" for temperature, "multiplicative" for precipitation.

    Returns
    -------
    np.ndarray
        Bias-corrected data.
    """
    if method == "additive":
        delta = np.mean(model_future) - np.mean(model_hist)
        corrected = observed + delta
    elif method == "multiplicative":
        hist_mean = np.mean(model_hist)
        if hist_mean > 0:
            ratio = np.mean(model_future) / hist_mean
        else:
            ratio = 1.0
        corrected = observed * ratio
    else:
        raise ValueError(f"Unknown method: {method}. Use 'additive' or 'multiplicative'.")

    return corrected
