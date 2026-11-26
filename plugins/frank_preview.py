"""Shared Frank v5.6 processing for the web preview and saved dataset."""
import hashlib
import logging
from pathlib import Path
from threading import RLock

import matplotlib.pyplot as plt
import numpy as np

from plugins.energy_sampling import describe_energy_sampling
from plugins.qc_presentation import figure_image
from plugins.read_data import ReadData
from quality_control.quality_check import CheckQuality

CRITERIA = Path(__file__).resolve().parents[1] / "quality_control" / "Criteria.json"
QC_PLOTS = (
    ("RAW", "Raw data"),
    ("NORMALIZED", "Normalized data"),
    ("k", "k"),
    ("R", "R"),
)
IMPORTED_PLOT = "Imported signals before QC calibration"
QC_PLOT_LABELS = {
    "Raw data": "Raw absorption",
    "Normalized data": "Normalized edge",
    "k": "EXAFS k²χ(k)",
    "R": "Fourier magnitude (no phase correction)",
}
# Matplotlib uses shared pyplot state and named figures in the QC engine.
_plot_lock = RLock()


def analyze_qc(path, source="SYNCHROTRON", column_selection=None, element=None, edge=None):
    input_sha256 = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    reader = ReadData(source=source, column_selection=column_selection)
    with _plot_lock:
        try:
            reader.process_data(path)
        finally:
            if hasattr(reader, "fig_raw_data"):
                plt.close(reader.fig_raw_data)

    imported = reader.data
    qc = CheckQuality(CRITERIA, element=element or None, edge=edge or None)
    qc.load_data(imported.copy(), source=reader.source, name=Path(path).name)
    try:
        qc.preprocess_data(take_first=True)
    except IndexError as exc:
        raise ValueError(
            "QC preprocessing could not finish with these inputs. "
            "Check the energy and detector columns or restore automatic selection."
        ) from exc

    checks = {}
    for key, check in (
        ("edge_step", qc.check_edge_step),
        ("energy_resolution", qc.check_energy_resolution),
        ("k_max", qc.check_k),
    ):
        passed, value = check()
        checks[key] = {"passed": bool(passed), "value": float(value)}
    report = {
        "file": Path(path).name,
        "qc_version": "Frank v5.6",
        "input_sha256": input_sha256,
        "status": "PASS" if all(check["passed"] for check in checks.values()) else "REVIEW",
        "checks": checks,
        "beamline": "Manual column selection" if column_selection else reader.beamline,
        "noise": float(qc.estimate_noise()[1]),
        "kmin": float(qc.kmin),
        "kmax": float(qc.kmax),
        "n_pts": int(len(qc.data.energy)),
        "raw_in_meta": {"raw_energy", "raw_mu"} <= reader.meta_data_dict.keys(),
        "energy_sampling": describe_energy_sampling(
            imported[0], qc.energy_calibration["uncalibrated_reference_eV"]
        ),
        "energy_calibration": qc.energy_calibration,
        "column_selection": reader.meta_data_dict.get("Column_selection"),
    }
    if not all(np.isfinite(value) for value in (
        report["noise"], report["kmin"], report["kmax"],
        *(check["value"] for check in checks.values()),
    )):
        raise ValueError("QC returned a non-finite result.")
    return qc, imported, report


def render_qc_plots(qc, imported, *, image_format="png"):
    plots = {}
    with _plot_lock:
        figure, ax = plt.subplots()
        try:
            energy, reference, sample = imported
            ax.plot(energy, sample, color="#276149", label="Sample / selected spectrum")
            ax.plot(energy, reference, color="#7565a8", linestyle="--", label="Reference")
            ax.set(xlabel="Input energy (eV)", ylabel="Selected absorption signal (a.u.)",
                   title=IMPORTED_PLOT)
            ax.legend()
            figure.tight_layout()
            plots[IMPORTED_PLOT] = figure_image(figure, image_format=image_format, tight=False)
        finally:
            plt.close(figure)

        for kind, caption in QC_PLOTS:
            try:
                figure = qc.plot_data(data_type=kind)
                plots[caption] = figure_image(figure, image_format=image_format)
            finally:
                if hasattr(qc, "fig_data"):
                    plt.close(qc.fig_data)
    return plots


def original_file_qc(path, source="SYNCHROTRON", column_selection=None, element=None, edge=None):
    try:
        qc, imported, report = analyze_qc(path, source, column_selection, element, edge)
        images = render_qc_plots(qc, imported)
        plots = [dict(label=QC_PLOT_LABELS.get(caption, caption), url=url)
                 for caption, url in images.items()]
        return dict(
            report=report,
            plots=plots,
            available=True,
            energy_min=float(imported[0, 0]),
            energy_max=float(imported[0, -1]),
            element=qc.data.element_n_edge[0],
            edge=qc.data.element_n_edge[1],
            source=qc.source,
            selection=report["column_selection"],
            input_digest=report["input_sha256"],
            input_label="Corrected columns" if column_selection else "Automatic columns",
        )
    except Exception as exc:
        logging.getLogger(__name__).exception("Original-file QC could not be completed for %s", path)
        return dict(available=False, error=f"QC could not be completed: {exc}")
