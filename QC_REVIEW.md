# RefXAS QC review

The review baseline is the locally extracted VM application source in commit
`aee6a26`. Its upstream Git revision is unconfirmed. The running VM image was
created on 7 October 2026 at 11:24:06 CEST and has no labels.

- Tag: `registry.hzdr.de/daphne4nfdi/xafsdb/refxas_beta2_test:curator-fix-2026-10-07`
- Image ID: `sha256:18649f2bcd0311eaf5a1d43a9cd0040dba8a53bba66086a3e87ac9bfb446d0cf`
- Registry digest: `sha256:0c7fc879aa25dec15e7bfc853f384677a624a25d7138a4ca746f69b50eed8889`

## QC change list

| File | Change |
| --- | --- |
| plugins/column_correction.py | Stores pending upload state and applies column corrections. |
| plugins/column_labels.py | Recovers column labels from source headers. |
| plugins/column_preview.py | Prepares preview data for column selection. |
| plugins/column_views.py | Handles scan and column application requests. |
| plugins/energy_sampling.py | Describes energy sampling for QC. |
| plugins/frank_preview.py | Runs QC and generates four plots for default or corrected inputs. |
| plugins/qc_presentation.py | Formats results and plots for display. |
| plugins/read_data.py | Extends file parsing and beamline detection. |
| plugins/selected_spectrum.py | Constructs a spectrum from the selected columns. |
| plugins/text_table.py | Parses text tables and scan data. |
| quality_control/quality_check.py | Adds edge resolution and QC handling for the integrated reader. |
| xafsdb_web/static/js/column_correction.js | Connects column controls to the preview and apply requests. |
| xafsdb_web/templates/landing/frank_panel.html | Renders QC results and plots. |
| xafsdb_web/templates/landing/verify.html | Integrates the QC panel and column controls into upload verification. |
| xafsdb_web/urls.py | Adds the scan and apply endpoints. |
| xafsdb_web/views.py | Integrates QC and corrected parameters into the upload workflow. |

Added endpoints are `/dataset/scan_columns` and `/dataset/apply_columns`.
The existing upload and verification routes keep their URLs and gain QC
integration. The QC commit contains no dependency, migration, deployment, or
SciCat client file changes against the extracted source.

Local storage is tracked separately. The candidate uses the URL `/media/`
and sets `MEDIA_ROOT` from `RAW_DATA_ROOT`, defaulting to `/raw_data_files`.
The production volume mapping remains to be verified.

## Local verification

Build from the review checkout with `docker build -t refxas-qc-review .`.
Use the resulting app image in the isolated local Docker Compose setup with
its test databases, SciCat configuration, and local media volume. Exercise
upload, verify, column scan, column apply, and final submission using test data.
Record detected beamline and edge, individual QC measurements and pass flags,
and plot count for each reference file.

Earlier tests on the larger candidate passed ten header cases and produced
matching QC values and four plots for SOLEIL SAMBA and PETRA III P65 across two
local images. The earlier standalone SLRI Cu foil run returned REVIEW with
energy-resolution criterion 9.93, edge step 1.809, k max 15, and noise 0.00234.
These are historical results. The isolated Docker results are recorded below.

## Separate curator change

The prior candidate sends a SciCat hard-delete request. Its reviewed-datasets
view checks curator-group membership and logs failures. Successful action
auditing and verification-state eligibility require implementation. Apply the
role check at every curator entry point, including list, details, and approval.
The soft-delete operation must preserve raw measurement files and block
published datasets. Record the actor, dataset, time, and reason. Verify the
curator account and negative permission cases in the isolated stack.

## Recorded standalone QC output

Only the status and checks fields are reproduced below. These runs used the earlier standalone QC workflow.
{
  "sample": "Cu2O_sample",
  "status": "PASS",
  "checks": {
    "edge_step": {
      "passed": true,
      "value": 0.6301421383976116
    },
    "energy_resolution": {
      "passed": true,
      "value": 0.4266738798614824
    },
    "k_max": {
      "passed": true,
      "value": 16.25
    },
    "noise": {
      "passed": true,
      "value": 0.0007861487933372872
    }
  }
}
{
  "sample": "Cu_SLRI_labels_fixed",
  "status": "REVIEW",
  "checks": {
    "edge_step": {
      "passed": true,
      "value": 1.809454672836348
    },
    "energy_resolution": {
      "passed": false,
      "value": 9.930000000000291,
      "label": "First energy interval (legacy Frank QC criterion)",
      "method": "energy[1] - energy[0]",
      "unit": "eV",
      "interpretation": "Scan spacing; not measured instrumental resolution"
    },
    "k_max": {
      "passed": true,
      "value": 15.0
    },
    "noise": {
      "passed": true,
      "value": 0.0023417510198431675
    }
  }
}

## Docker QC output for build tag e6fee50

Both files were available and each generated four plots. Both detected the Cu K edge at 8979.0 eV. The Arial warning did not interrupt plot generation.

| File | Status | Edge step | First energy interval (eV) | k max | Noise |
| --- | --- | ---: | ---: | ---: | ---: |
| Cu2O Cu K Elettra.txt | REVIEW | 0.8581219462105223 (pass) | 4.99688900000001 (fail) | 14.0 (fail) | 0.0006769070442764328 (pass) |
| Cu foil Cu K SLRI | REVIEW | 1.8094543482724703 (pass) | 9.930000000000291 (fail) | 15.0 (pass) | 0.002343054024949011 (pass) |

Both runs used automatic column selection. The earlier PASS used a different Cu2O file, Cu2O_Cu_K_0000.xdi, and explicit column selection. The positive control using that original input and selection is documented below.

### Cu2O positive control with explicit columns

The isolated Docker build selected Yb L2 at 9978 eV for Cu2O_Cu_K_0000.xdi using energy_enc, i0, i1, and log_ratio with automatic edge detection. Larch autobk then raised ValueError: cannot convert float NaN to integer. QC was unavailable and generated zero plots. The earlier standalone PASS has not been reproduced in this build.

## Scope for the current review

Dataset deletion is deferred. The QC change excludes curator deletion and curator access changes. A separate local safeguard draft makes the reviewed-datasets page read-only and applies a shared curator-group check to list, details, approval, and reviewed-datasets routes. That draft is pending runtime verification and is outside this review and any deployment.

## Edge-selection fix and Docker rerun — 21 November 2026

The column-correction path previously selected the last qualifying derivative peak.
For the Cu2O control that was 9977.02 eV and led to the incorrect Yb L2
assignment. The corrected path selects the strongest qualifying interior peak.
The existing first-peak mode continues to use its original selection rule.

| Control | Expected / actual | Edge (eV) | Edge step | Legacy interval (eV) | k max | Noise | Plots |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cu2O Cu K | PASS / PASS | Cu K (8979) | 0.63014 | 0.42667 | 16.25 | 0.00078881 | 4 |
| P65 Au foil | PASS / PASS | Au L3 (11919) | 1.80089 | 0.64620 | 15.35 | 0.00036184 | 4 |
| SLRI Cu foil | REVIEW / REVIEW | Cu K (8979) | 1.80945 | 9.93000 (fail) | 15.00 | 0.00234305 | 4 |

All three results matched their expected edge and status, and runtime
reported no QC errors. The Cu2O peak was 8968.34 eV before calibration.
The local evidence includes results.json and four PNGs per control.
Matplotlib warned about Arial availability and still generated all plots.
