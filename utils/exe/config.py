from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

ConfigValue = Union[str, bool]

DEFAULT_CONFIG: Dict[str, ConfigValue] = {
    "debug": False,
    "webServer": False,  # <-- FLAG WEBSERVER
    "autoPlcIp": False,
    "logToFile": False,
    "downloadOnStart": True,
    "lastUrl": "",
    "defaultWorkingFolder": "_PGSXF",
    "defaultSaveFolder": "saved_configs",
    "defaultDownloadFolder": "downloaded_configs",
    "loginEnabled": True,
    "sessionCookies": "",
}


def _clean_relative_folder(value: Any, fallback: str) -> Path:
    """
    Ritorna un path relativo sicuro, impedendo a save/download folder di
    uscire dalla defaultWorkingFolder.
    """
    raw = str(value or fallback).strip() or fallback
    p = Path(raw)

    if p.is_absolute() or any(part in ("..", "") for part in p.parts):
        p = Path(fallback)

    return p


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "y", "on", "si", "sì")
    return bool(value)


def _coerce_config(raw_cfg: Any) -> Dict[str, ConfigValue]:
    """Unisce il config letto da disco con i default, mantenendo solo le chiavi note."""
    if not isinstance(raw_cfg, dict):
        raw_cfg = {}

    cfg: Dict[str, ConfigValue] = DEFAULT_CONFIG.copy()
    for key, default_value in DEFAULT_CONFIG.items():
        value = raw_cfg.get(key, default_value)
        if isinstance(default_value, bool):
            cfg[key] = _to_bool(value)
        else:
            cfg[key] = str(value) if value is not None else str(default_value)

    # defaultDownloadFolder e defaultSaveFolder devono restare sotto defaultWorkingFolder.
    cfg["defaultDownloadFolder"] = str(
        _clean_relative_folder(cfg.get("defaultDownloadFolder"), str(DEFAULT_CONFIG["defaultDownloadFolder"]))
    )
    cfg["defaultSaveFolder"] = str(
        _clean_relative_folder(cfg.get("defaultSaveFolder"), str(DEFAULT_CONFIG["defaultSaveFolder"]))
    )

    return cfg


def _read_json(path: Path) -> Dict[str, ConfigValue] | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            raw_cfg = json.load(f)
        return _coerce_config(raw_cfg)
    except Exception:
        return None


def _working_folder_from_config(cfg: Dict[str, ConfigValue] | None = None) -> Path:
    folder = str((cfg or DEFAULT_CONFIG).get("defaultWorkingFolder") or DEFAULT_CONFIG["defaultWorkingFolder"]).strip()
    if not folder:
        folder = str(DEFAULT_CONFIG["defaultWorkingFolder"])

    p = Path(folder)
    if not p.is_absolute():
        p = Path.cwd() / p

    return p


def get_working_folder(cfg: Dict[str, ConfigValue] | None = None, create: bool = True) -> Path:
    """Cartella base applicativa: contiene config.json e le sottocartelle operative."""
    p = _working_folder_from_config(cfg)
    if create:
        p.mkdir(parents=True, exist_ok=True)
    return p


def get_download_folder(cfg: Dict[str, ConfigValue] | None = None, create: bool = True) -> Path:
    """Cartella download sotto defaultWorkingFolder: config.yaml, config_old_*.yaml, temp."""
    cfg = cfg or load_exe_config()
    base = get_working_folder(cfg, create=create)
    rel = _clean_relative_folder(cfg.get("defaultDownloadFolder"), str(DEFAULT_CONFIG["defaultDownloadFolder"]))
    p = base / rel
    if create:
        p.mkdir(parents=True, exist_ok=True)
    return p


def get_save_folder(cfg: Dict[str, ConfigValue] | None = None, create: bool = True) -> Path:
    """Cartella salvataggi manuali sotto defaultWorkingFolder."""
    cfg = cfg or load_exe_config()
    base = get_working_folder(cfg, create=create)
    rel = _clean_relative_folder(cfg.get("defaultSaveFolder"), str(DEFAULT_CONFIG["defaultSaveFolder"]))
    p = base / rel
    if create:
        p.mkdir(parents=True, exist_ok=True)
    return p


def get_exe_config_path() -> Path:
    """Ritorna il percorso del file config.json dentro defaultWorkingFolder."""
    default_cfg_path = get_working_folder(DEFAULT_CONFIG, create=True) / "config.json"

    if default_cfg_path.exists():
        cfg = _read_json(default_cfg_path)
        if cfg is not None:
            normalized_path = get_working_folder(cfg, create=True) / "config.json"
            if normalized_path.exists():
                return normalized_path
        return default_cfg_path

    # Compatibilita' con versioni precedenti: se esiste ./config.json lo migro
    # nella defaultWorkingFolder indicata da quel file, altrimenti uso _PGSXF.
    legacy_cfg_path = Path.cwd() / "config.json"
    if legacy_cfg_path.exists():
        legacy_cfg = _read_json(legacy_cfg_path) or DEFAULT_CONFIG.copy()
        return get_working_folder(legacy_cfg, create=True) / "config.json"

    # Se defaultWorkingFolder e' stato personalizzato in un avvio precedente,
    # prova a ritrovare un config.json di primo livello sotto la cwd.
    for candidate in sorted(Path.cwd().glob("*/config.json")):
        cfg = _read_json(candidate)
        if cfg is None:
            continue
        normalized_path = get_working_folder(cfg, create=True) / "config.json"
        if candidate.resolve() == normalized_path.resolve():
            return candidate

    return default_cfg_path


def _write_config_file(path: Path, cfg: Dict[str, ConfigValue]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def save_exe_config(cfg: Dict[str, ConfigValue], path: str | Path | None = None) -> None:
    """Salva la configurazione nel file config.json dentro defaultWorkingFolder."""
    cfg = _coerce_config(cfg)
    p = Path(path) if path is not None else get_working_folder(cfg, create=True) / "config.json"
    _write_config_file(p, cfg)

    # Bootstrap: se il working folder viene personalizzato, mantieni aggiornato
    # anche il config nel working folder di default per ritrovare il path custom
    # al prossimo avvio.
    if path is None:
        bootstrap_path = get_working_folder(DEFAULT_CONFIG, create=True) / "config.json"
        if p.resolve() != bootstrap_path.resolve() and bootstrap_path.exists():
            _write_config_file(bootstrap_path, cfg)


def load_exe_config(path: str | Path | None = None) -> Dict[str, ConfigValue]:
    """
    Carica la configurazione dell'applicazione.

    Se il file non esiste, crea config.json in defaultWorkingFolder.
    Se trova un vecchio ./config.json, lo legge e lo copia nel nuovo percorso.
    """
    if path is not None:
        p = Path(path)
        cfg = _read_json(p)
        if cfg is None:
            cfg = DEFAULT_CONFIG.copy()
            save_exe_config(cfg, p)
            return cfg
        normalized_path = get_working_folder(cfg, create=True) / "config.json"
        if p.resolve() != normalized_path.resolve():
            save_exe_config(cfg, normalized_path)
        return cfg

    p = get_exe_config_path()

    if not p.exists():
        legacy_cfg_path = Path.cwd() / "config.json"
        legacy_cfg = _read_json(legacy_cfg_path) if legacy_cfg_path.exists() else None
        cfg = legacy_cfg or DEFAULT_CONFIG.copy()
        save_exe_config(cfg, p)
        return cfg.copy()

    cfg = _read_json(p)
    if cfg is None:
        cfg = DEFAULT_CONFIG.copy()
        save_exe_config(cfg, p)
        return cfg.copy()

    # Riscrive il file se mancavano chiavi nuove o se sono state normalizzate.
    save_exe_config(cfg, p)

    # Se defaultWorkingFolder dentro il config punta altrove, assicura che esista
    # anche il config nel path corretto. Non elimino il vecchio file: puo' servire
    # come bootstrap per ritrovare una defaultWorkingFolder personalizzata.
    normalized_path = get_working_folder(cfg, create=True) / "config.json"
    if p.resolve() != normalized_path.resolve():
        save_exe_config(cfg, normalized_path)

    return cfg.copy()


def get_param(name: str) -> ConfigValue:
    """Restituisce il parametro `name` dal config applicativo."""
    if name not in DEFAULT_CONFIG:
        raise KeyError(f"Parametro non riconosciuto: {name}")
    cfg = load_exe_config()
    return cfg.get(name, DEFAULT_CONFIG[name])


def update_param(name: str, value: ConfigValue) -> None:
    """Aggiorna il parametro `name` nel config applicativo."""
    if name not in DEFAULT_CONFIG:
        raise KeyError(f"Parametro non riconosciuto: {name}")
    cfg = load_exe_config()
    cfg[name] = value
    save_exe_config(cfg)
