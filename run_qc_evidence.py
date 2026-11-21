"""Run the RefXAS QC review controls and save the reported plots and metrics."""

import base64
import json
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

from plugins.frank_preview import original_file_qc


def main():
    fixtures = Path("quality_control/example data/SYNCHROTRON")
    output = Path("/evidence")
    cases = [
        ("cu2o", Path("/control/Cu2O_Cu_K_0000.xdi"), "PASS", ("Cu", "K"),
         {"energy": "energy_enc", "signal_a": "i0", "signal_b": "i1", "formula": "log_ratio"}),
        ("p65", fixtures / "Au foil_Au L3 P65 DESY.xdi", "PASS", ("Au", "L3"), None),
        ("slri", fixtures / "Cu foil Cu K SLRI", "REVIEW", ("Cu", "K"), None),
    ]
    report = []
    for name, path, expected, expected_edge, selection in cases:
        result = original_file_qc(path, column_selection=selection)
        folder = output / name
        folder.mkdir(parents=True, exist_ok=False)
        plots = []
        for label, plot in zip(("raw", "normalized", "k", "R"), result.get("plots", [])):
            image = folder / f"{label}.png"
            image.write_bytes(base64.b64decode(plot["url"].split(",", 1)[1], validate=True))
            plots.append(str(image.relative_to(output)))
        metrics = result.get("report", {})
        edge = (result.get("element"), result.get("edge"))
        report.append({
            "file": path.name,
            "expected_status": expected,
            "actual_status": metrics.get("status"),
            "expected_edge": expected_edge,
            "actual_edge": edge,
            "checks": metrics.get("checks"),
            "energy_sampling": metrics.get("energy_sampling"),
            "plots": plots,
            "error": result.get("error"),
            "matched": metrics.get("status") == expected and edge == expected_edge and len(plots) == 4,
        })
    payload = json.dumps(report, indent=2, allow_nan=False)
    (output / "results.json").write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if all(row["matched"] for row in report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
