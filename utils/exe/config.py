import json
from pathlib import Path
from typing import Dict

DEFAULT_CONFIG: Dict[str, bool] = {
    "debug": False,
    "webServer": False,  # <-- FLAG WEBSERVER
    "autoPlcIp": False,
    "logToFile": False,
}


def get_exe_config_path() -> Path:
    """Ritorna il percorso del file config.json."""
    return Path.cwd() / "config.json"


def save_exe_config(cfg: Dict[str, bool], path: str | Path | None = None) -> None:
    """Salva la configurazione nel file config.json."""
    p = Path(path) if path is not None else get_exe_config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def load_exe_config(path: str | Path | None = None) -> Dict[str, bool]:
    """
    Carica la configurazione dal file config.json.
    Se il file non esiste, lo crea con i valori di default.
    """
    p = Path(path) if path is not None else get_exe_config_path()
    if not p.exists():
        save_exe_config(DEFAULT_CONFIG, p)
        return DEFAULT_CONFIG.copy()
    try:
        with p.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
            if not isinstance(cfg, dict):
                raise ValueError("config.json non è un oggetto JSON valido")
    except Exception:
        save_exe_config(DEFAULT_CONFIG, p)
        return DEFAULT_CONFIG.copy()

    changed = False
    for k, v in DEFAULT_CONFIG.items():
        if k not in cfg:
            cfg[k] = v
            changed = True
    if changed:
        save_exe_config(cfg, p)

    return {k: bool(cfg.get(k, v)) for k, v in DEFAULT_CONFIG.items()}
