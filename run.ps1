$ErrorActionPreference = "Stop"
$python = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"

if (Test-Path $python) {
    & $python main.py @args
} else {
    python main.py @args
}
