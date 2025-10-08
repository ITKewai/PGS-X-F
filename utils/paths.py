# utils/paths.py
from __future__ import annotations
from pathlib import Path
import sys
import os


def is_frozen() -> bool:
    """Rileva se stiamo girando come EXE (PyInstaller)."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def exe_dir() -> Path:
    """Cartella dove si trova l'eseguibile (o lo script entry-point)."""
    return Path(sys.executable).parent if is_frozen() else Path(__file__).resolve().parent.parent


def resource_path(rel: str | Path) -> Path:
    """
    Percorso a risorse impacchettate (PyInstaller). In dev cade su percorso relativo al repo.
    Usa per file SOLO-LETTURA inclusi nel bundle.
    """
    rel = Path(rel)
    if is_frozen():
        return Path(sys._MEIPASS) / rel  # type: ignore[attr-defined]
    return exe_dir() / rel


def get_run_dir(prefer_cwd: bool = True) -> Path:
    """
    Cartella di lavoro "effettiva" da usare per file letti/scritti dall'utente.
    - prefer_cwd=True -> usa SEMPRE la cartella da cui l'utente lancia il programma (Path.cwd()).
    - prefer_cwd=False -> usa la cartella dell'eseguibile/script (exe_dir()).
    """
    return Path.cwd() if prefer_cwd else exe_dir()


def ensure_dir(p: Path) -> Path:
    """Crea la cartella se manca (safe). Ritorna p."""
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_config_path(filename: str = "config.yaml", prefer_cwd: bool = True) -> Path:
    """Percorso al config nella run dir (quella che vuoi tu)."""
    return get_run_dir(prefer_cwd=prefer_cwd) / filename


def in_run_subdir(*parts: str, prefer_cwd: bool = True, create: bool = False) -> Path:
    """
    Percorso dentro una sottocartella della run dir (es. logs/, cache/).
    """
    p = get_run_dir(prefer_cwd=prefer_cwd).joinpath(*parts)
    return ensure_dir(p) if create else p
