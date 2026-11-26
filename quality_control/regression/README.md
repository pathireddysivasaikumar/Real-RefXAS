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

## KIT deployment candidate

The [KIT verification results](evidence/kit-results.json) document the
candidate checked on this branch. It includes Sebastian's ESRF linked-channel
fix and the original H5 fixture. ROCK and ESRF retain the QC values and REVIEW
verdicts from the KIT review baseline at `53d03e8`. Both Cu₂O submission
modes returned PASS and matched Frank's calibration. The ESRF curator ZIP
contains the original H5 file byte for byte.

- [Corrected Cu₂O curator report](evidence/kit-cu2o-run-002-curator.png)
- [ROCK Mo foil curator report](evidence/kit-rock-mo-curator.png)
- [ESRF H5 curator report](evidence/kit-esrf-h5-curator.png)

## Earlier November 2026 verification evidence

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
