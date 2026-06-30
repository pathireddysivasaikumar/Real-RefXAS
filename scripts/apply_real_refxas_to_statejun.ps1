# Real refXAS apply helper
# Run from the folder that contains your StateJun xafsdb repo.
# Example: C:\Users\jg7371\Desktop\XAS\master

$ErrorActionPreference = "Stop"

$Repo = ".\xafsdb"
$Real = ".\Real_refXAS"

if (!(Test-Path $Repo)) { throw "Cannot find StateJun repo folder: $Repo" }
if (!(Test-Path $Real)) { throw "Cannot find Real_refXAS folder: $Real" }

cd $Repo
git checkout -b real-refxas-statejun-v5-quality
cd ..

$Files = @(
  "auto_dataset_create.py",
  "auto_bl_create.py",
  "plugins\read_data.py",
  "plugins\__init__.py",
  "quality_control\quality_check.py",
  "quality_control\data_check.py",
  "quality_control\requirements.txt",
  "quality_control\__init__.py",
  "xafsdb_web\views.py",
  "xafsdb_web\urls.py",
  "xafsdb_web\utils.py",
  "webserver\settings.py",
  "webserver\urls.py",
  "xafsdb_deployment\docker-compose.yaml",
  "xafsdb_deployment\.env.example"
)

foreach ($f in $Files) {
  $src = Join-Path $Real $f
  $dst = Join-Path $Repo $f
  $dstDir = Split-Path $dst -Parent
  if (!(Test-Path $dstDir)) { New-Item -ItemType Directory -Force -Path $dstDir | Out-Null }
  Copy-Item $src $dst -Force
}

Copy-Item "$Real\xafsdb_web\templates" "$Repo\xafsdb_web\" -Recurse -Force
Copy-Item "$Real\xafsdb_web\static" "$Repo\xafsdb_web\" -Recurse -Force
Copy-Item "$Real\materials" "$Repo\" -Recurse -Force

cd $Repo
python -m py_compile auto_dataset_create.py plugins/read_data.py quality_control/quality_check.py auto_bl_create.py xafsdb_web/views.py xafsdb_web/urls.py xafsdb_web/utils.py webserver/settings.py webserver/urls.py

git status
Write-Host "Real refXAS merge files copied. Review git diff before commit." -ForegroundColor Green
