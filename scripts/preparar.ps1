$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
    Write-Host 'Creado .env a partir del ejemplo. Configura HTTPS_PROXY si tu red lo necesita.'
}
. (Join-Path $PSScriptRoot 'entorno.ps1')
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'Instala uv antes de preparar el proyecto.' }
Write-Host 'uv sync --locked: restaura el entorno Python a partir de uv.lock.'
uv sync --locked
if ($LASTEXITCODE -ne 0) { throw 'No se pudo restaurar el entorno Python.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host 'Instalando Node.js 24 localmente desde nodejs-wheel (distribucion de terceros en PyPI).'
    uv tool install --python 3.13 'nodejs-wheel==24.19.0'
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo instalar Node.js.' }
}
$wheelDirectory = Join-Path $root '.tools\uv-tools\nodejs-wheel\Lib\site-packages\nodejs_wheel'
if (Test-Path -LiteralPath (Join-Path $wheelDirectory 'node.exe')) {
    foreach ($toolName in @('npm', 'npx')) {
        $launcher = '@ECHO OFF' + "`r`n" + '"%~dp0node.exe" "%~dp0lib\node_modules\npm\bin\' + $toolName + '-cli.js" %*' + "`r`n"
        [IO.File]::WriteAllText((Join-Path $wheelDirectory ($toolName + '.cmd')), $launcher, [Text.Encoding]::ASCII)
    }
}
. (Join-Path $PSScriptRoot 'entorno.ps1')
node -v
if ($LASTEXITCODE -ne 0) { throw 'Node.js no esta disponible.' }
npm.cmd -v
if ($LASTEXITCODE -ne 0) { throw 'npm no esta disponible.' }
if ($env:HTTPS_PROXY) {
    Write-Host 'Configurando proxy y https-proxy de npm con HTTPS_PROXY, sin copiar su valor al archivo.'
    npm.cmd config set proxy '${HTTPS_PROXY}' --location=user --loglevel=error
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo configurar el proxy de npm.' }
    npm.cmd config set https-proxy '${HTTPS_PROXY}' --location=user --loglevel=error
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo configurar https-proxy de npm.' }
}
Set-Location -LiteralPath (Join-Path $root 'web')
Write-Host 'npm ci: instala exactamente las versiones de package-lock.json.'
npm.cmd ci
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias web.' }
Write-Host 'npm run build: compila la interfaz para que tambien pueda servirla FastAPI.'
npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'No se pudo compilar la interfaz.' }
Set-Location -LiteralPath $root
Write-Host 'Proyecto preparado. Ejecuta .\iniciar.ps1'
