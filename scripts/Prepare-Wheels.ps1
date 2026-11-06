param([Parameter(Mandatory=$true)][string]$PythonExe,[Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Path $Destination -Force|Out-Null
& $PythonExe -m pip download --only-binary=:all: -r (Join-Path $PSScriptRoot '..\vendor\strata\requirements.txt') --dest $Destination
if($LASTEXITCODE -ne 0){throw 'Wheel download failed. Use Windows x64 / Python 3.11.'}