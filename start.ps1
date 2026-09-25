$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

foreach ($port in 8000, 8501) {
    $pids = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($procId in $pids) {
        try {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        } catch {}
    }
}

if (Test-Path "$root\.venv\Scripts\Activate.ps1") {
    . "$root\.venv\Scripts\Activate.ps1"
}

python .\run_app.py
