$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'entorno.ps1')
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
Write-Host 'uv run python -m pytest: verifica API, evidencias, recuentos y fechas.'
$testRun = '.runtime/tests/' + [guid]::NewGuid().ToString('N')
uv run python -m pytest -q --tb=short --basetemp ($testRun + '/tmp') -o ('cache_dir=' + $testRun + '/cache')
if ($LASTEXITCODE -ne 0) { throw 'Hay pruebas de la API que no pasan.' }
Set-Location -LiteralPath (Join-Path $root 'web')
Write-Host 'npm run check: verifica Svelte y TypeScript.'
npm.cmd run check
if ($LASTEXITCODE -ne 0) { throw 'La comprobacion de Svelte/TypeScript ha fallado.' }
Write-Host 'npm run build: verifica la compilacion.'
npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'La compilacion ha fallado.' }
Set-Location -LiteralPath $root
Write-Host 'Todas las comprobaciones han pasado.'
