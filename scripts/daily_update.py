#!/usr/bin/env python3
"""Daily ESGF node availability checker for CMIP6 data pipeline.

Pings major ESGF data nodes, records response times, updates a
status markdown report and a historical availability heatmap.
"""

import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import requests

# ── ESGF data nodes (THREDDS / OPeNDAP endpoints) ──────────────────────────
NODES = {
    "LLNL (USA)": "https://esgf-node.llnl.gov/thredds/catalog.html",
    "DKRZ (Germany)": "https://esgf-data.dkrz.de/thredds/catalog.html",
    "IPSL (France)": "https://esgf-node.ipsl.upmc.fr/thredds/catalog.html",
    "NCI (Australia)": "https://esgf.nci.org.au/thredds/catalog.html",
    "CEDA (UK)": "https://esgf-index1.ceda.ac.uk/thredds/catalog.html",
    "CMCC (Italy)": "https://esgf-node.cmcc.it/thredds/catalog.html",
}

TIMEOUT_S = 10
SLOW_THRESHOLD_MS = 5000

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
STATUS_MD = DOCS_DIR / "esgf-status.md"
HISTORY_CSV = DOCS_DIR / "esgf-history.csv"
CHART_PNG = DOCS_DIR / "esgf-availability.png"


def check_node(name: str, url: str) -> dict:
    """Ping a single node and return status info."""
    try:
        start = time.monotonic()
        resp = requests.head(url, timeout=TIMEOUT_S, allow_redirects=True)
        elapsed_ms = round((time.monotonic() - start) * 1000)

        if resp.status_code < 400:
            status = "slow" if elapsed_ms > SLOW_THRESHOLD_MS else "online"
        else:
            status = "offline"
    except requests.RequestException:
        elapsed_ms = -1
        status = "offline"

    return {
        "node": name,
        "url": url,
        "status": status,
        "response_ms": elapsed_ms,
    }


def load_previous_status() -> dict[str, str]:
    """Return {node: status} from the last row per node in history CSV."""
    prev: dict[str, str] = {}
    if not HISTORY_CSV.exists():
        return prev
    with open(HISTORY_CSV, newline="") as fh:
        for row in csv.DictReader(fh):
            prev[row["node"]] = row["status"]
    return prev


def append_history(results: list[dict], now: str) -> None:
    """Append today's results to the history CSV."""
    write_header = not HISTORY_CSV.exists() or HISTORY_CSV.stat().st_size == 0
    with open(HISTORY_CSV, "a", newline="") as fh:
        writer = csv.writer(fh)
        if write_header:
            writer.writerow(["date", "node", "status", "response_ms"])
        for r in results:
            writer.writerow([now, r["node"], r["status"], r["response_ms"]])


def write_status_md(results: list[dict], now: str) -> None:
    """Write the human-readable status markdown."""
    status_icon = {"online": "🟢", "slow": "🟡", "offline": "🔴"}
    lines = [
        "# ESGF Node Availability Status",
        "",
        f"_Last checked: {now} UTC_",
        "",
        "| Node | URL | Status | Response (ms) |",
        "|------|-----|--------|---------------|",
    ]
    for r in results:
        icon = status_icon.get(r["status"], "⚪")
        ms = r["response_ms"] if r["response_ms"] >= 0 else "—"
        lines.append(f"| {r['node']} | {r['url']} | {icon} {r['status']} | {ms} |")

    lines += [
        "",
        "---",
        "",
        "![Availability timeline](esgf-availability.png)",
    ]
    STATUS_MD.write_text("\n".join(lines) + "\n")


def generate_chart() -> None:
    """Create a heatmap of node availability over time from the history CSV."""
    if not HISTORY_CSV.exists():
        return

    rows: list[dict] = []
    with open(HISTORY_CSV, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return

    # Parse unique dates and nodes
    dates_str = sorted(set(r["date"] for r in rows))
    nodes = list(NODES.keys())

    dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates_str]
    date_idx = {d: i for i, d in enumerate(dates_str)}
    node_idx = {n: i for i, n in enumerate(nodes)}

    status_map = {"online": 1.0, "slow": 0.5, "offline": 0.0}
    grid = np.full((len(nodes), len(dates)), np.nan)

    for r in rows:
        ni = node_idx.get(r["node"])
        di = date_idx.get(r["date"])
        if ni is not None and di is not None:
            grid[ni, di] = status_map.get(r["status"], np.nan)

    fig, ax = plt.subplots(figsize=(max(6, len(dates) * 0.35), 4))
    cmap = plt.cm.RdYlGn  # red → yellow → green
    im = ax.imshow(grid, aspect="auto", cmap=cmap, vmin=0, vmax=1, interpolation="nearest")

    ax.set_yticks(range(len(nodes)))
    ax.set_yticklabels(nodes, fontsize=8)

    # Show date labels (limit to ~20 labels max)
    step = max(1, len(dates) // 20)
    tick_positions = list(range(0, len(dates), step))
    ax.set_xticks(tick_positions)
    ax.set_xticklabels([dates_str[i] for i in tick_positions], rotation=45, ha="right", fontsize=7)

    ax.set_title("ESGF Node Availability", fontsize=11, pad=10)
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 0.5, 1], shrink=0.8)
    cbar.ax.set_yticklabels(["offline", "slow", "online"], fontsize=8)

    fig.tight_layout()
    fig.savefig(str(CHART_PNG), dpi=150)
    plt.close(fig)


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"Checking ESGF nodes — {now}")
    results = [check_node(name, url) for name, url in NODES.items()]
    for r in results:
        print(f"  {r['node']:20s}  {r['status']:7s}  {r['response_ms']} ms")

    # Detect if anything changed since last recorded check
    prev = load_previous_status()
    changed = any(r["status"] != prev.get(r["node"]) for r in results)
    if prev:
        print(f"Status changed since last check: {changed}")
    else:
        changed = True  # first run always writes

    append_history(results, now)
    write_status_md(results, now)
    generate_chart()

    if not changed:
        # Revert docs so git sees no diff → workflow won't commit
        import subprocess
        subprocess.run(["git", "checkout", "--", "docs/"], check=False)
        print("No status change — reverted docs to avoid empty commit.")

    print("Done.")


if __name__ == "__main__":
    main()
