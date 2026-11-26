"""Run the shared QC over measurement files and write the results as JSON."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
QC_ROOT = Path(__file__).resolve().parents[1]
if str(QC_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(QC_ROOT.parent))

from plugins.frank_preview import analyze_qc, render_qc_plots


def run_example(path):
    try:
        qc, imported, report = analyze_qc(path)
        plots = render_qc_plots(qc, imported)
        if len(plots) != 5 or any(len(image) < 500 for image in plots.values()):
            raise ValueError("QC did not produce five valid plots.")
        calibration = report["energy_calibration"]
        return {
            **report,
            "e0": round(calibration["reference_e0_eV"], 3),
            "edge_step": round(report["checks"]["edge_step"]["value"], 5),
            "edge_ok": report["checks"]["edge_step"]["passed"],
            "eres_ok": report["checks"]["energy_resolution"]["passed"],
            "k_ok": report["checks"]["k_max"]["passed"],
            "spectrometer_shift_eV": calibration["spectrometer_shift_eV"],
            "edge_shift_eV": calibration["edge_shift_eV"],
        }
    except Exception as exc:
        return {
            "status": "ERROR",
            "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
            "ERROR": f"{type(exc).__name__}: {exc}",
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=Path("results.json"))
    parser.add_argument("measurements", nargs="*", type=Path)
    args = parser.parse_args()
    sample_dir = QC_ROOT / "example data" / "SYNCHROTRON"
    measurements = args.measurements or sorted(
        path for path in sample_dir.iterdir()
        if path.is_file() and path.suffix not in (".zip", ".gitkeep")
    )
    results = {str(path) if args.measurements else path.name: run_example(path)
               for path in measurements}
    args.output.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
