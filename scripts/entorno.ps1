# Cargar con: . .\scripts\entorno.ps1
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$portableNode = Get-ChildItem -LiteralPath (Join-Path $projectRoot '.tools') -Directory -Filter 'node-*-win-x64' -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
if ($portableNode) {
    $env:PATH = $portableNode.FullName + [IO.Path]::PathSeparator + $env:PATH
}
$wheelNodeDirectory = Join-Path $projectRoot '.tools\uv-tools\nodejs-wheel\Lib\site-packages\nodejs_wheel'
if (-not $portableNode -and (Test-Path -LiteralPath (Join-Path $wheelNodeDirectory 'node.exe'))) {
    $env:PATH = $wheelNodeDirectory + [IO.Path]::PathSeparator + $env:PATH
}
$environmentFile = Join-Path $projectRoot '.env'
if (Test-Path -LiteralPath $environmentFile) {
    foreach ($line in [IO.File]::ReadAllLines($environmentFile)) {
        if ($line -match '^\s*(?:export\s+)?(HTTPS_PROXY|HTTP_PROXY|NO_PROXY)\s*=\s*(.*?)\s*$') {
            $variableName = $Matches[1]
            $variableValue = $Matches[2].Trim()
            if (($variableValue.StartsWith('"') -and $variableValue.EndsWith('"')) -or ($variableValue.StartsWith("'") -and $variableValue.EndsWith("'"))) {
                $variableValue = $variableValue.Substring(1, $variableValue.Length - 2)
            }
            [Environment]::SetEnvironmentVariable($variableName, $variableValue, 'Process')
        }
    }
}
if ($env:HTTPS_PROXY -and -not $env:HTTP_PROXY) { $env:HTTP_PROXY = $env:HTTPS_PROXY }
# Both development servers communicate locally, without passing through a proxy.
$env:NO_PROXY = (@($env:NO_PROXY -split ',') + @('localhost', '127.0.0.1', '::1') | Where-Object { $_ } | Select-Object -Unique) -join ','
$env:NPM_CONFIG_USERCONFIG = Join-Path $projectRoot '.npmrc'
$env:UV_CACHE_DIR = Join-Path $projectRoot '.cache\uv'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $projectRoot '.tools\python'
$env:UV_SYSTEM_CERTS = 'true'
$env:UV_TOOL_DIR = Join-Path $projectRoot '.tools\uv-tools'
$env:UV_TOOL_BIN_DIR = Join-Path $projectRoot '.tools\bin'
$env:NPM_CONFIG_CACHE = Join-Path $projectRoot '.cache\npm'
$env:NODE_USE_SYSTEM_CA = '1'
