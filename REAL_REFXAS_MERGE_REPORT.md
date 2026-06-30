# Real refXAS — StateJun + V5 Value Merge

Generated: 2026-06-30

## Base rule

StateJun is preserved as the deployment and developer baseline. V5 was not copied blindly. Only high-value scientific, QC, upload, curator, export, and beamline improvements were merged.

## Included V5 value

- V5 `plugins/read_data.py` with `.dat`, `.xdi`, `.spec`, `.h5`, `.hdf`, `.hdf5`, `.nxs`, and `.nexus` routing.
- V5 `quality_control/quality_check.py` with stronger Larch QC, edge step, energy resolution, k/R plots, normalized plots, and QC controller.
- Backward-compatible aliases: `read_data = ReadData`, `check_quality = CheckQuality`, and `check_quality_control = CheckQualityControl`.
- V5 header extraction into the verification page.
- V5 curator dataset list/detail/approval pages.
- V5 ZIP export from dataset details with metadata and plots.
- V5 beamline/instrument pages and beamline creation flow.
- V5 improved search utilities and `snake_case_to_title_case` helper.
- V5 templates and visual improvements, while preserving StateJun `/contact`.
- StateJun-safe Docker/VM structure with persistent MongoDB and private Postgres.

## Intentionally not included

- V5 `.env` and StateJun `.env` files.
- V5 `db.sqlite3`.
- V5 `startup_patch.py` as a production mechanism.
- V5 temporary upload files and NAS sync logs.
- V5 test bundles and generated `hdf5_zip_check` bundles.
- Generated MkDocs static `docs/` output. The source can be added later if documentation hosting is required.

## Most important changed files

- `auto_dataset_create.py`
- `auto_bl_create.py`
- `plugins/read_data.py`
- `quality_control/quality_check.py`
- `xafsdb_web/views.py`
- `xafsdb_web/urls.py`
- `xafsdb_web/utils.py`
- `webserver/settings.py`
- `webserver/urls.py`
- `xafsdb_deployment/docker-compose.yaml`
- `xafsdb_web/templates/landing/*`

## Production principle

For the KIT VM, do not use runtime patching. This package mounts the merged source files cleanly into the existing xafsdb container. Later, the best final step is building a proper image named something like `real-refxas:kit-vm`.
