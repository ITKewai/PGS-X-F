# utils/paths.py
from __future__ import annotations

from pathlib import Path
import sys

from utils.exe.config import get_download_folder, get_working_folder


def is_frozen() -> bool:
    """
    Verifica se l'applicazione è in esecuzione come eseguibile PyInstaller.

    PyInstaller imposta l'attributo `sys.frozen` e crea la cartella temporanea
    `sys._MEIPASS` quando l'app viene eseguita da un bundle.
    """
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def exe_dir() -> Path:
    """
    Restituisce la cartella dell'eseguibile o la root del progetto.
    """
    return Path(sys.executable).parent if is_frozen() else Path(__file__).resolve().parent.parent


def resource_path(rel: str | Path) -> Path:
    """
    Costruisce il percorso assoluto a una risorsa inclusa nell'applicazione.
    """
    rel = Path(rel)
    if is_frozen():
        return Path(sys._MEIPASS) / rel  # type: ignore[attr-defined]
    return exe_dir() / rel


def get_run_dir(prefer_cwd: bool = True) -> Path:
    """
    Restituisce la cartella di lavoro applicativa per file runtime.

    Nota: `prefer_cwd` resta per compatibilità con il codice esistente, ma i
    file runtime non vengono più messi direttamente nella cwd: vengono messi
    sotto defaultWorkingFolder.
    """
    return get_working_folder(create=True)


def ensure_dir(p: Path) -> Path:
    """Crea una cartella se non esiste già."""
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_config_path(filename: str = "config.yaml", prefer_cwd: bool = True) -> Path:
    """
    Restituisce il percorso dei file YAML scaricati/operativi.

    I file `config.yaml`, `config_temp.yaml` e `config_old_*.yaml` stanno sotto:
        defaultWorkingFolder/defaultDownloadFolder/
    """
    return get_download_folder(create=True) / filename


def in_run_subdir(*parts: str, prefer_cwd: bool = True, create: bool = False) -> Path:
    """
    Costruisce un percorso dentro defaultWorkingFolder.
    """
    p = get_run_dir(prefer_cwd=prefer_cwd).joinpath(*parts)
    return ensure_dir(p) if create else p
