# ---------------------------------------------------------------------------
# setup_venv.ps1 — create + activate this project's NAMED venv on Windows.
# (macOS / Linux / WSL: use setup_venv.sh instead.)
#
#   . .\setup_venv.ps1          # <- DOT-SOURCE it so the activation sticks
#
# Why the leading dot? Like `source` in bash, dot-sourcing runs the script in
# YOUR PowerShell session, so the (aja-cca-f) prefix appears in your prompt and
# stays. Running it plainly (.\setup_venv.ps1) builds the venv and installs
# deps, but the activation is lost when the script's child scope exits.
#
# If PowerShell blocks the script ("running scripts is disabled"), run:
#   powershell -ExecutionPolicy Bypass -File setup_venv.ps1
# (that variant builds + installs; then activate manually with the line printed
#  at the end).
# ---------------------------------------------------------------------------

$ErrorActionPreference = 'Stop'
$VenvName = 'aja-cca-f'

Set-Location $PSScriptRoot

# Find a Python launcher: prefer `python`, fall back to the `py` launcher.
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
if (-not $py) {
  Write-Host "Python 3.10+ was not found on your PATH. Install it from python.org, then re-run." -ForegroundColor Red
  return
}

# Create the venv once; reuse it on later runs.
if (-not (Test-Path $VenvName)) {
  Write-Host "Creating named venv:   $VenvName"
  & $py.Source -m venv $VenvName
} else {
  Write-Host "Reusing existing venv: $VenvName"
}

# Activate it in THIS session.
& ".\$VenvName\Scripts\Activate.ps1"

# Install dependencies into the venv.
python -m pip install --quiet --upgrade pip
pip install -r requirements.txt

# Scaffold .env for the Anthropic key if it isn't there yet (never overwrites).
if ((-not (Test-Path .env)) -and (Test-Path .env.example)) {
  Copy-Item .env.example .env
  Write-Host "Created .env from .env.example - add your ANTHROPIC_API_KEY."
}

Write-Host ""
Write-Host "Done. If your prompt shows ($VenvName), the venv is active." -ForegroundColor Green
Write-Host "If it does NOT, dot-source this script so activation sticks:" -ForegroundColor Yellow
Write-Host "    . .\setup_venv.ps1"
Write-Host "Or activate manually:   .\$VenvName\Scripts\Activate.ps1"
Write-Host "Deactivate anytime with:  deactivate"
