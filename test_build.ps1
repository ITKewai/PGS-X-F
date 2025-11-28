# powershell -ExecutionPolicy Bypass -File .\test_build.ps1
# build_all_versions.ps1
# Script locale per buildare tutte le versioni:
# - prende tutti i tia_constants_*.py in tia_exports/**/
# - li copia su utils/exports/tia_constants.py
# - rigenera version_info.txt
# - builda un EXE per ognuno con nome PSG-X-Finder-Beta-VERSIONE

# Fermati se qualcosa va storto
$ErrorActionPreference = "Stop"

Write-Host ">>> Script build_all_versions.ps1 avviato..."

# Vai nella cartella dove sta lo script (radice repo)
Set-Location $PSScriptRoot

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

# Backup dello spec originale
Write-Host ">>> Faccio il backup di test.spec in test.spec.bak"
Copy-Item "test.spec" "test.spec.bak" -Force

# Cerca tutti i tia_constants_*.py sotto tia_exports
$tiaFiles = Get-ChildItem "tia_exports" -Recurse -Filter "tia_constants_*.py"

if (-not $tiaFiles) {
    Write-Error "Nessun file 'tia_constants_*.py' trovato in 'tia_exports'."
}

foreach ($file in $tiaFiles) {
    # Es: tia_constants_0_25_40_1.py -> 0_25_40_1
    $version = $file.BaseName -replace '^tia_constants_',''

    Write-Host ""
    Write-Host "==============================================="
    Write-Host ">>> Build per versione PLC: $version"
    Write-Host "    File sorgente: $($file.FullName)"
    Write-Host "==============================================="

    # 1) Copia tia_constants_X in utils/exports/tia_constants.py
    Write-Host ">>> Copio $($file.Name) in utils/exports/tia_constants.py"
    Copy-Item $file.FullName "utils/exports/tia_constants.py" -Force

    # 2) Rigenera version_info.txt (se lo usi in PyInstaller)
    Write-Host ">>> Rigenero version_info.txt con make_version_file.py"
    python make_version_file.py

    if ($LASTEXITCODE -ne 0) {
        Write-Error "make_version_file.py ha fallito per versione $version (exit code $LASTEXITCODE)."
    }

    # 3) Rigenera test.spec partendo SEMPRE dal backup originale
    Write-Host ">>> Aggiorno test.spec per nome eseguibile PSG-X-Finder-Beta-$version"
    (Get-Content "test.spec.bak") -replace "PSG-X-Finder-Beta", "PSG-X-Finder-Beta-$version" |
        Set-Content "test.spec"

    # 4) Lancia PyInstaller
    Write-Host ">>> Lancio PyInstaller per versione $version ..."
    pyinstaller "test.spec" --noconfirm

    if ($LASTEXITCODE -ne 0) {
        Write-Error "PyInstaller ha fallito per versione $version (exit code $LASTEXITCODE)."
    }

    Write-Host ">>> Build per versione $version COMPLETATA."
}

# Ripristina lo spec originale
Write-Host ""
Write-Host ">>> Ripristino test.spec originale da test.spec.bak"
Copy-Item "test.spec.bak" "test.spec" -Force

Write-Host ">>> Tutte le build completate. Controlla la cartella 'dist'."
