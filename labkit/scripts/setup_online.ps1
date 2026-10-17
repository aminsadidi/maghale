# setup_online.ps1 - ONE-TIME setup while the PC is connected to the internet.
# Downloads everything the lab kit needs into labkit\vendor so that the simulations later run fully offline:
#   portable Python 3.11 (only if no usable Python is installed), numpy/matplotlib wheels, the MNPBEM17 toolbox.
# Then detects MATLAB / Lumerical / COMSOL (with licence tests) and prints the simulation plan with a first time estimate.
# Usage: double-click SETUP_ONLINE.bat  (or: powershell -ExecutionPolicy Bypass -File scripts\setup_online.ps1)
$ErrorActionPreference = 'Stop'
$KIT = Split-Path -Parent $PSScriptRoot
$V = Join-Path $KIT 'vendor'
New-Item -ItemType Directory -Force -Path $V, (Join-Path $V 'wheels'), (Join-Path $KIT 'output') | Out-Null
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
function Get-File($url, $dst) {
    for ($i = 1; $i -le 3; $i++) {
        try { Invoke-WebRequest -Uri $url -OutFile $dst -UseBasicParsing; return } catch { Write-Host "  retry $i ($url)"; Start-Sleep -Seconds (5 * $i) }
    }
    throw "download failed: $url"
}

Write-Host "`n[1/5] internet" -ForegroundColor Cyan
try { Invoke-WebRequest -Uri 'https://pypi.org/simple/numpy/' -UseBasicParsing -TimeoutSec 20 | Out-Null; Write-Host '  OK' }
catch { Write-Host '  NO INTERNET - connect the PC and run this again.' -ForegroundColor Red; exit 1 }

Write-Host "`n[2/5] Python" -ForegroundColor Cyan
$py = $null
$cands = @(@{exe = 'py'; args = @('-3')}, @{exe = 'python'; args = @()})
foreach ($c in $cands) {
    try {
        $v = & $c.exe @($c.args) -c "import sys; print('%d.%d' % sys.version_info[:2]); print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $v -and [version]$v[0] -ge [version]'3.9') {
            # private virtual environment: no admin rights needed, nothing installed system-wide
            $venv = Join-Path $V 'venv'
            if (-not (Test-Path (Join-Path $venv 'Scripts\python.exe'))) { & $v[1] -m venv $venv }
            $py = Join-Path $venv 'Scripts\python.exe'; break
        }
    } catch {}
}
if (-not $py) {
    Write-Host '  no usable Python found -> downloading portable Python 3.11.9 (about 10 MB)'
    $pdir = Join-Path $V 'python'
    Get-File 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' (Join-Path $V 'python.zip')
    Expand-Archive -Force (Join-Path $V 'python.zip') $pdir
    $pth = Get-ChildItem $pdir -Filter 'python*._pth' | Select-Object -First 1
    (Get-Content $pth.FullName) -replace '^#\s*import site', 'import site' | Set-Content $pth.FullName
    Get-File 'https://bootstrap.pypa.io/get-pip.py' (Join-Path $V 'get-pip.py')
    & (Join-Path $pdir 'python.exe') (Join-Path $V 'get-pip.py') --no-warn-script-location
    $py = Join-Path $pdir 'python.exe'
}
Set-Content -Path (Join-Path $V 'python_path.txt') -Value $py -Encoding ASCII
Write-Host "  using $py"

Write-Host "`n[3/5] Python packages (kept in vendor\wheels for offline re-install)" -ForegroundColor Cyan
& $py -m pip download numpy matplotlib -d (Join-Path $V 'wheels') --quiet
& $py -m pip install --no-index --find-links (Join-Path $V 'wheels') numpy matplotlib --quiet
Write-Host '  OK'

Write-Host "`n[4/5] MNPBEM17 toolbox (GPL-2.0)" -ForegroundColor Cyan
$mdir = Join-Path $V 'MNPBEM'
if (-not (Test-Path (Join-Path $mdir 'Material'))) {
    Get-File 'https://codeload.github.com/Nikolaos-Matthaiakakis/MNPBEM/zip/refs/heads/main' (Join-Path $V 'mnpbem.zip')
    Expand-Archive -Force (Join-Path $V 'mnpbem.zip') $V
    if (Test-Path $mdir) { Remove-Item -Recurse -Force $mdir }
    Rename-Item (Join-Path $V 'MNPBEM-main') 'MNPBEM'
}
Write-Host '  OK'

Write-Host "`n[5/5] detecting MATLAB / Lumerical / COMSOL (licence tests take a few minutes) and planning" -ForegroundColor Cyan
Push-Location $KIT
& $py (Join-Path $KIT 'lab\runner.py') plan --redetect
Pop-Location
Write-Host "`nSetup finished. The internet is no longer needed. Next: double-click RUN.bat" -ForegroundColor Green
