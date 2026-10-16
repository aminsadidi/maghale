# check_pc.ps1 - reports what the lab PC offers for the simulations (read-only: it changes nothing).
# Usage (PowerShell):  powershell -ExecutionPolicy Bypass -File check_pc.ps1
# Writes the report to the screen and to pc_report.txt next to this script.
$out = @()
function Add($s) { $script:out += $s; Write-Host $s }

Add "=== System ==="
$os = Get-CimInstance Win32_OperatingSystem
Add ("OS          : {0} {1} (build {2})" -f $os.Caption, $os.OSArchitecture, $os.BuildNumber)
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
Add ("CPU         : {0}, {1} cores / {2} threads" -f $cpu.Name.Trim(), $cpu.NumberOfCores, $cpu.NumberOfLogicalProcessors)
$ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
Add ("RAM         : $ram GB")
Get-CimInstance Win32_VideoController | ForEach-Object { Add ("GPU         : {0}" -f $_.Name) }
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    Add ("Disk {0}     : {1} GB free of {2} GB" -f $_.DeviceID, [math]::Round($_.FreeSpace / 1GB), [math]::Round($_.Size / 1GB)) }

Add ""; Add "=== Simulation software ==="
function FindDirs($patterns) {
    $hits = @()
    foreach ($p in $patterns) { $hits += Get-ChildItem -Path $p -Directory -ErrorAction SilentlyContinue }
    return $hits
}
$m = Get-Command matlab -ErrorAction SilentlyContinue
if ($m) { Add "MATLAB (PATH): $($m.Source)" } else { Add "MATLAB (PATH): not on PATH" }
FindDirs @("C:\Program Files\MATLAB\*", "D:\Program Files\MATLAB\*", "C:\MATLAB\*") | ForEach-Object { Add "MATLAB found: $($_.FullName)" }
FindDirs @("C:\Program Files\COMSOL\*", "D:\Program Files\COMSOL\*") | ForEach-Object { Add "COMSOL found: $($_.FullName)" }
FindDirs @("C:\Program Files\Lumerical\*", "C:\Program Files\ANSYS Inc\*\Lumerical*", "C:\Program Files\Ansys Inc\*\Lumerical*", "D:\Program Files\Lumerical\*") |
    ForEach-Object { Add "Lumerical found: $($_.FullName)" }

Add ""; Add "=== Tools ==="
foreach ($t in @("git", "python", "py", "wsl")) {
    $c = Get-Command $t -ErrorAction SilentlyContinue
    if ($c) { Add ("{0,-11} : {1}" -f $t, $c.Source) } else { Add ("{0,-11} : not found" -f $t) }
}
$out | Set-Content -Encoding UTF8 (Join-Path $PSScriptRoot "pc_report.txt")
Add ""; Add "Report saved to pc_report.txt - please send this file."
