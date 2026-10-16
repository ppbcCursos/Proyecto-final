$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'entorno.ps1')
Set-Location -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'web')
Write-Host 'Interfaz Vite: http://127.0.0.1:5173'
npm.cmd run dev
