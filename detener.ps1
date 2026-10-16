$ErrorActionPreference = 'Stop'
$manifestPath = Join-Path $PSScriptRoot '.runtime\processes.json'
if (-not (Test-Path -LiteralPath $manifestPath)) { Write-Host 'No hay procesos de Folio registrados.'; return }
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.project -ne $PSScriptRoot) { throw 'El registro de procesos pertenece a otra carpeta.' }
foreach ($service in $manifest.services) {
    $ownedProcess = Get-Process -Id $service.pid -ErrorAction SilentlyContinue
    if ($ownedProcess -and $ownedProcess.StartTime.ToUniversalTime().Ticks -eq $service.started_utc_ticks) {
        Write-Host ('Deteniendo ' + $service.name + ' de este proyecto.')
        taskkill.exe /PID $service.pid /T /F | Out-Null
    }
}
Remove-Item -LiteralPath $manifestPath
Write-Host 'Folio detenido.'
