# bootstrap.ps1 - downloads the project (with the lab kit) to C:\maghale_lab and starts the online setup.
# Run in PowerShell:
#   iwr https://raw.githubusercontent.com/aminsadidi/maghale/claude/sleepy-rubin-e80q4k/labkit/bootstrap.ps1 -OutFile $env:TEMP\bootstrap.ps1; powershell -ExecutionPolicy Bypass -File $env:TEMP\bootstrap.ps1
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$dst = 'C:\maghale_lab'
$zip = Join-Path $env:TEMP 'maghale.zip'
Write-Host "downloading the project to $dst ..."
Invoke-WebRequest -UseBasicParsing -OutFile $zip -Uri 'https://codeload.github.com/aminsadidi/maghale/zip/refs/heads/claude/sleepy-rubin-e80q4k'
$tmp = Join-Path $env:TEMP 'maghale_x'
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
Expand-Archive -Force $zip $tmp
$src = Get-ChildItem $tmp | Select-Object -First 1
New-Item -ItemType Directory -Force -Path $dst | Out-Null
# keep earlier results and downloads if the kit was installed before
robocopy $src.FullName $dst /E /XD output vendor /NFL /NDL /NJH /NJS | Out-Null
Write-Host "project copied to $dst"
powershell -ExecutionPolicy Bypass -File (Join-Path $dst 'labkit\scripts\setup_online.ps1')
