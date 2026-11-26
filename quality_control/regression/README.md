# QC regression checks

From the repository root, use the installed RefXAS Python environment to run
the shared QC calculation and write `results.json`:

```shell
python -m quality_control.regression.run_examples results.json
python -m pytest -q -rxX test/test_frank_qc.py
```

The runner checks the synchrotron examples by default. To run specific files,
pass their paths after the JSON destination. Each successful result includes
the source SHA-256, calibrated and uncalibrated edge energies, spectrometer
energy shift, sample–reference shift, QC verdict, and scan spacing.

The SLRI fixture starts at roughly 9.93 eV spacing and has roughly 0.30 eV
spacing near the edge. The strict expected-failure test records the difference
between the current first-interval check and the proposed near-edge criterion.
The test will flag an unexpected pass so the expectation can be revisited when
the criterion changes.

## November 2026 verification evidence

The [results JSON](evidence/results.json) records the original file hashes, QC
checks, and both energy shifts. Browser verification used an isolated local
SciCat server and covered upload, preview, saved report, curator view, and ZIP
download. The same branch was also checked in an offline container with the
pinned xraylarch version. Both runtimes reproduced the reference calibration
and verdict. Floating-point noise values can differ below the displayed precision.

- [Cu₂O run_002 curator view](evidence/cu2o-run-002-curator.png)
- [Independent Elettra Cu₂O control](evidence/cu2o-elettra-curator.png)

The Elettra scan is REVIEW under the current first-interval and available
k-range criteria. The KIT VM was left untouched.
