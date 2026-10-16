$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
. (Join-Path $root 'scripts\entorno.ps1')
Add-Type -AssemblyName System.Net.Http

function Test-LocalPort([int]$port) {
    $client = New-Object Net.Sockets.TcpClient
    try { $pending = $client.ConnectAsync('127.0.0.1', $port); return ($pending.Wait(400) -and $client.Connected) }
    catch { return $false }
    finally { $client.Dispose() }
}
foreach ($port in @(8000, 5173)) {
    if (Test-LocalPort $port) { throw "El puerto $port ya esta ocupado. Si Folio esta iniciado, abre http://127.0.0.1:5173; para reiniciarlo usa detener.ps1." }
}
$nodeCommand = Get-Command node.exe -ErrorAction Stop
$uvCommand = Get-Command uv.exe -ErrorAction Stop
$viteFile = Join-Path $root 'web\node_modules\vite\bin\vite.js'
if (-not (Test-Path -LiteralPath $viteFile)) { throw 'Faltan dependencias. Ejecuta .\scripts\preparar.ps1.' }
$runtime = Join-Path $root '.runtime'
New-Item -ItemType Directory -Path $runtime -Force | Out-Null
$services = @()
try {
    $backend = Start-Process -FilePath $uvCommand.Source -ArgumentList @('run', 'python', '-m', 'uvicorn', 'folio.api:app', '--host', '127.0.0.1', '--port', '8000', '--reload', '--reload-dir', 'src') -WorkingDirectory $root -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'backend.out.log') -RedirectStandardError (Join-Path $runtime 'backend.err.log')
    $services += @{ pid = $backend.Id; started_utc_ticks = $backend.StartTime.ToUniversalTime().Ticks; name = 'backend' }
    $frontend = Start-Process -FilePath $nodeCommand.Source -ArgumentList @(('"' + $viteFile + '"'), '--host', '127.0.0.1', '--port', '5173', '--strictPort') -WorkingDirectory (Join-Path $root 'web') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'web.out.log') -RedirectStandardError (Join-Path $runtime 'web.err.log')
    $services += @{ pid = $frontend.Id; started_utc_ticks = $frontend.StartTime.ToUniversalTime().Ticks; name = 'web' }
    @{ project = $root; services = $services } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $runtime 'processes.json') -Encoding UTF8
    $handler = [Net.Http.HttpClientHandler]::new()
    $handler.UseProxy = $false
    $http = [Net.Http.HttpClient]::new($handler)
    $http.Timeout = [TimeSpan]::FromSeconds(1)
    $ready = $false
    $deadline = (Get-Date).AddSeconds(25)
    try {
        while ((Get-Date) -lt $deadline) {
            try {
                $apiResponse = $http.GetAsync('http://127.0.0.1:8000/api/health').GetAwaiter().GetResult()
                $webResponse = $http.GetAsync('http://127.0.0.1:5173/').GetAwaiter().GetResult()
                $ready = $apiResponse.IsSuccessStatusCode -and $webResponse.IsSuccessStatusCode
                $apiResponse.Dispose(); $webResponse.Dispose()
                if ($ready) { break }
            } catch { }
            Start-Sleep -Milliseconds 300
        }
    } finally { $http.Dispose(); $handler.Dispose() }
    if (-not $ready) { throw 'No se pudo iniciar Folio. Revisa los registros de .runtime/.' }
    Write-Host 'Folio esta funcionando en http://127.0.0.1:5173'
    Write-Host 'API y documentacion: http://127.0.0.1:8000/docs'
    Write-Host 'Para detener ambos servicios: .\detener.ps1'
} catch {
    foreach ($service in $services) {
        $ownedProcess = Get-Process -Id $service.pid -ErrorAction SilentlyContinue
        if ($ownedProcess -and $ownedProcess.StartTime.ToUniversalTime().Ticks -eq $service.started_utc_ticks) {
            taskkill.exe /PID $service.pid /T /F | Out-Null
        }
    }
    throw
}
