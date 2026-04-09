"""Multi-server failover logic for ESGF data retrieval."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


class FailoverManager:
    """Manage failover across multiple ESGF data nodes.

    Automatically retries failed requests on alternative servers,
    tracks node health, and selects the fastest available node.
    """

    def __init__(
        self,
        nodes: list[str],
        max_retries: int = 3,
        backoff_factor: float = 1.5,
    ) -> None:
        self.nodes = nodes
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.node_health: dict[str, float] = {n: 1.0 for n in nodes}

    def execute_with_failover(
        self,
        operation: Callable[[str], Any],
    ) -> Any:
        """Execute an operation with automatic node failover.

        Parameters
        ----------
        operation : callable
            Function that takes a node URL and returns data.

        Returns
        -------
        Any
            Result from the first successful node.

        Raises
        ------
        ConnectionError
            If all nodes fail.
        """
        sorted_nodes = sorted(
            self.nodes, key=lambda n: self.node_health.get(n, 0), reverse=True
        )

        last_error = None
        for node in sorted_nodes:
            for attempt in range(self.max_retries):
                try:
                    result = operation(node)
                    self.node_health[node] = min(self.node_health.get(node, 0) + 0.1, 1.0)
                    return result
                except Exception as e:
                    last_error = e
                    self.node_health[node] = max(self.node_health.get(node, 1.0) - 0.3, 0)
                    wait = self.backoff_factor ** attempt
                    logger.warning(
                        "Node %s attempt %d failed: %s. Retrying in %.1fs",
                        node, attempt + 1, e, wait,
                    )
                    time.sleep(wait)

        raise ConnectionError(f"All ESGF nodes failed. Last error: {last_error}")
