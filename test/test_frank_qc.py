import hashlib
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

from plugins.frank_preview import analyze_qc

EXAMPLES = Path(__file__).resolve().parents[1] / "quality_control" / "example data" / "SYNCHROTRON"


@pytest.fixture(scope="module")
def slri_report():
    return analyze_qc(EXAMPLES / "Cu foil Cu K SLRI")[2]


def test_elettra_cu2o_reports_calibration_and_source_fingerprint():
    path = EXAMPLES / "Cu2O Cu K Elettra.txt"
    _, _, report = analyze_qc(path)
    calibration = report["energy_calibration"]

    assert report["input_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert calibration["detected_edge"] == "Cu K at 8979.000 eV"
    assert calibration["reference_e0_eV"] == pytest.approx(8979)
    assert calibration["sample_e0_eV"] - calibration["reference_e0_eV"] == pytest.approx(
        calibration["edge_shift_eV"]
    )


def test_slri_report_distinguishes_scan_start_and_near_edge_sampling(slri_report):
    sampling = slri_report["energy_sampling"]
    assert sampling["first_interval"] == pytest.approx(9.93)
    assert sampling["near_edge_median_interval"] == pytest.approx(0.30, abs=0.03)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="SLRI meets the near-edge spacing range, but the QC rule checks the first interval.",
)
def test_slri_energy_spacing_check_should_accept_near_edge_sampling(slri_report):
    assert slri_report["checks"]["energy_resolution"]["passed"]
