$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'entorno.ps1')
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
Write-Host 'Servidor Python: http://127.0.0.1:8000'
uv run python -m uvicorn folio.api:app --host 127.0.0.1 --port 8000 --reload --reload-dir src
