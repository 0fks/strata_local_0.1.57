[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Root)
$ErrorActionPreference='Stop'
$c=Get-Content -LiteralPath (Join-Path $Root 'server.json') -Raw|ConvertFrom-Json
if($c.host -ne '0.0.0.0'){throw 'This installation does not enable LAN access'}
$name='StrataLocal-LAN-'+$c.port
if(Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue){Write-Host 'Rule already exists. Inspect it before changing.';return}
New-NetFirewallRule -Name $name -DisplayName "Strata Local LAN TCP $($c.port)" -Direction Inbound -Action Allow -Protocol TCP -LocalPort $c.port -RemoteAddress LocalSubnet -Profile Private