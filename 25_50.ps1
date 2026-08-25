# build_0_25_50.ps1
# Script locale per buildare SOLO la versione PLC 0_25_50

$ErrorActionPreference = "Stop"

Write-Host ">>> Script build_0_25_50.ps1 avviato..."

# Vai nella cartella dove sta lo script, cioè la root del repo
Set-Location $PSScriptRoot
$root = $PSScriptRoot

$version = "0_25_50_0"
$exeName = "PGS-X-Finder-Beta-$version"

# Controlli base
if (-not (Test-Path "test.spec")) {
    Write-Error "test.spec non trovato nella cartella corrente: $(Get-Location)"
}

if (-not (Test-Path "make_version_file.py")) {
    Write-Error "make_version_file.py non trovato nella cartella corrente."
}

if (-not (Test-Path "utils/exports")) {
    Write-Error "Cartella 'utils/exports' non trovata."
}

if (-not (Test-Path "tia_exports")) {
    Write-Error "Cartella 'tia_exports' non trovata."
}

# Cerca SOLO tia_constants_0_25_50.py sotto tia_exports
$tiaFile = Get-ChildItem "tia_exports" -Recurse -Filter "tia_constants_$version.py" | Select-Object -First 1

if (-not $tiaFile) {
    Write-Error "File 'tia_constants_$version.py' non trovato sotto 'tia_exports'."
}

# Backup dello spec originale
Write-Host ">>> Faccio il backup di test.spec in test.spec.bak"
Copy-Item "test.spec" "test.spec.bak" -Force

try {
    Write-Host ""
    Write-Host "==============================================="
    Write-Host ">>> Build per versione PLC: $version"
    Write-Host "    File sorgente: $($tiaFile.FullName)"
    Write-Host "==============================================="

    # 1) Copia tia_constants_0_25_50.py in utils/exports/tia_constants.py
    Write-Host ">>> Copio $($tiaFile.Name) in utils/exports/tia_constants.py"
    Copy-Item $tiaFile.FullName "utils/exports/tia_constants.py" -Force

    # 2) Rigenera version_info.txt
    Write-Host ">>> Rigenero version_info.txt con make_version_file.py"
    python make_version_file.py

    if ($LASTEXITCODE -ne 0) {
        Write-Error "make_version_file.py ha fallito per versione $version (exit code $LASTEXITCODE)."
    }

    # 3) Rigenera test.spec partendo dal backup originale
    Write-Host ">>> Aggiorno test.spec per nome eseguibile $exeName"
    (Get-Content "test.spec.bak") -replace "PGS-X-Finder-Beta", $exeName |
        Set-Content "test.spec"

    # 4) Workpath dedicata per questa versione
    $workPath = Join-Path $root "build\test_$version"

    if (Test-Path $workPath) {
        Write-Host ">>> Pulisco workpath '$workPath'..." -ForegroundColor DarkYellow
        Remove-Item $workPath -Recurse -Force -ErrorAction SilentlyContinue
    }

    # 5) Lancia PyInstaller
    Write-Host ">>> Lancio PyInstaller per versione $version ..."
    pyinstaller ".\test.spec" --noconfirm --workpath "$workPath"

    if ($LASTEXITCODE -ne 0) {
        Write-Error "PyInstaller ha fallito per versione $version (exit code $LASTEXITCODE)."
        exit $LASTEXITCODE
    }

    Write-Host ">>> Build per versione $version COMPLETATA."
}
finally {
    # Ripristina sempre lo spec originale
    if (Test-Path "test.spec.bak") {
        Write-Host ""
        Write-Host ">>> Ripristino test.spec originale da test.spec.bak"
        Copy-Item "test.spec.bak" "test.spec" -Force
    }
}

Write-Host ">>> Build singola completata. Controlla la cartella 'dist'."

# Apre la cartella dist a fine build
$distPath = Join-Path $root "dist"

if (Test-Path $distPath) {
    Write-Host ">>> Apro la cartella dist..."
    Invoke-Item $distPath
} else {
    Write-Warning "Cartella 'dist' non trovata: $distPath"
}