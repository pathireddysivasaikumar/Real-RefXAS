#!/usr/bin/env python3
"""Static integration validation that does not require Django/Larch services."""
from __future__ import annotations
from pathlib import Path
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
warnings: list[str] = []

# 1. Compile every Python source in memory (no __pycache__ side effects).
compiled = 0
for path in ROOT.rglob("*.py"):
    if "__pycache__" in path.parts:
        continue
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        compile(source, str(path), "exec")
        compiled += 1
    except Exception as exc:
        errors.append(f"Python compile failed: {path.relative_to(ROOT)}: {exc}")

# 2. Parse active key modules and verify compatibility contracts.
read_data = (ROOT / "plugins/read_data.py").read_text(encoding="utf-8")
quality = (ROOT / "quality_control/quality_check.py").read_text(encoding="utf-8")
auto_ds = (ROOT / "auto_dataset_create.py").read_text(encoding="utf-8")
auto_bl = (ROOT / "auto_bl_create.py").read_text(encoding="utf-8")
for label, text in [("read_data", read_data), ("quality_check", quality), ("auto_dataset_create", auto_ds), ("auto_bl_create", auto_bl)]:
    try:
        ast.parse(text)
    except SyntaxError as exc:
        errors.append(f"AST parse failed for {label}: {exc}")

checks = {
    "ReadData compatibility alias": "read_data = ReadData" in read_data,
    "ReadData Path normalization": "self.data_path = Path(data_path)" in read_data,
    "HDF suffix handling": "['.h5', '.hdf', '.hdf5']" in read_data,
    "QC legacy alias": "check_quality = CheckQuality" in quality,
    "QC controller legacy alias": "check_quality_control = CheckQualityControl" in quality,
    "Container SciCat endpoint": "SCICAT_API_URL" in auto_ds and "SCICAT_API_URL" in auto_bl,
    "No retired GCP endpoint in auto dataset": "34.29.91.220" not in auto_ds,
    "No retired GCP endpoint in auto beamline": "34.29.91.220" not in auto_bl,
}
for name, ok in checks.items():
    if not ok:
        errors.append(f"Contract check failed: {name}")

# 3. Deployment file existence.
required = [
    "xafsdb_deployment/docker-compose.yaml",
    "xafsdb_deployment/config/backend/config.env",
    "xafsdb_deployment/config/backend/functionalAccounts.json",
    "xafsdb_deployment/config/xafsdb/_auth_constants.py",
    ".env.vm.example",
    "MERGE_FILE_MANIFEST.csv",
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f"Required file missing: {rel}")

# 4. YAML syntax check if PyYAML is available.
try:
    import yaml
    compose = ROOT / "xafsdb_deployment/docker-compose.yaml"
    with compose.open("r", encoding="utf-8") as fh:
        parsed = yaml.safe_load(fh)
    if not isinstance(parsed, dict) or "services" not in parsed:
        errors.append("docker-compose.yaml parsed but has no services mapping")
except ModuleNotFoundError:
    warnings.append("PyYAML unavailable; docker-compose YAML syntax not checked")
except Exception as exc:
    errors.append(f"docker-compose.yaml parse failed: {exc}")

# 5. Known security/deployment warnings (not automatic failures because they require coordinated rotation).
compose_text = (ROOT / "xafsdb_deployment/docker-compose.yaml").read_text(encoding="utf-8")
if "POSTGRES_PASSWORD=" in compose_text:
    warnings.append("Historical compose still contains a static PostgreSQL password; rotate/externalize before VM production deployment")
if "--api.insecure=true" in compose_text:
    warnings.append("Traefik insecure API is enabled in historical compose; restrict before public deployment")

print(f"Compiled Python files: {compiled}")
for warning in warnings:
    print(f"WARNING: {warning}")
if errors:
    for error in errors:
        print(f"ERROR: {error}")
    sys.exit(1)
print("RESULT: PASS (static integration checks). Runtime service/QC validation is still required on a dependency-complete staging environment.")
