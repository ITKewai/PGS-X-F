#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo per gestire il download del file config.yaml.
Compatibile con i percorsi e le logiche di PSG-X-FindIndex.
"""

from __future__ import annotations
from pathlib import Path
import requests
import warnings as _warnings
from urllib3.exceptions import InsecureRequestWarning

from utils.paths import get_config_path

_warnings.simplefilter("ignore", InsecureRequestWarning)

last_url = ''


def _build_download_url(addr: str) -> str:
    """
    Costruisce l'URL finale per scaricare il config.
    Accetta:
      - 10.3.73.177
      - http://10.3.73.177
      - https://10.3.73.177
      - https://10.3.73.177/UserFiles?Name=config.yaml&Action=DOWNLOAD
    """
    addr = addr.strip()
    path = "/UserFiles?Name=config.yaml&Action=DOWNLOAD"

    if "://" in addr:
        if "UserFiles" in addr or "?" in addr:
            return addr
        return addr.rstrip("/") + path
    return f"https://{addr}{path}"


def download_file(url: str, dest_path: Path) -> None:
    """
    Scarica il file da un URL e lo salva in dest_path.
    Se HTTPS fallisce, prova HTTP in fallback.
    """
    print("🌐 Download in corso...")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        r = requests.get(url, timeout=60, verify=False)
        r.raise_for_status()
        dest_path.write_bytes(r.content)
    except Exception as e_https:
        # Fallback HTTP
        try:
            if url.startswith("https://"):
                url_http = "http://" + url[len("https://"):]
                r = requests.get(url_http, timeout=60)
                r.raise_for_status()
                dest_path.write_bytes(r.content)
            else:
                raise
        except Exception as e_http:
            raise RuntimeError(f"Errore nel download:\nHTTPS: {e_https}\nHTTP: {e_http}") from e_http

    print(f"✅ File salvato in: {dest_path}")


def _download_to_config(url: str) -> Path:
    """
    Scarica su <cwd>/config.yaml, facendo prima un backup in config_old.yaml.
    Se config_old.yaml esiste già, viene sovrascritto con l'attuale config.yaml.
    """
    global last_url
    cfg_path = get_config_path("config.yaml", prefer_cwd=True)
    backup_path = cfg_path.with_name("config_old.yaml")

    # --- Backup automatico ---
    if cfg_path.exists():
        try:
            # se esiste config_old.yaml, sovrascrivi
            backup_path.write_bytes(cfg_path.read_bytes())
            print(f"📦 Backup aggiornato: {backup_path}")
        except Exception as e:
            print(f"⚠️ Errore durante il backup: {e}")

    # --- Download nuovo file ---
    download_file(url, cfg_path)
    last_url = url
    return cfg_path


def choose_and_prepare_config() -> Path:
    """
    Chiede all'utente se usare il config locale o scaricarlo.
    Ritorna il percorso finale del file pronto.
    """
    global last_url

    cfg_path = get_config_path("config.yaml", prefer_cwd=True)

    while True:
        print("\nSelezione sorgente file 'config.yaml'")
        print("  [1] Usa file locale (cartella corrente)")
        print("  [2] Scarica file da rete")
        if last_url:
            print("  [3] Aggiorna file da rete (ultimo URL)")

        choice = input("Scelta: ").strip()

        if choice == "2":
            base = input("Inserisci indirizzo/IP (es: 10.3.73.177): ").strip()
            if not base:
                print("Indirizzo non valido.\n")
                continue

            url = _build_download_url(base)
            try:
                return _download_to_config(url)
            except Exception:
                print("❌ Errore nel download")
                continue

        elif choice == "1":
            if cfg_path.exists():
                return cfg_path
            print(f"❌ File locale non trovato o corrotto: {cfg_path}\n")
            continue

        elif choice == "3" and last_url:
            res = fetch_again()
            if res is not None:
                return res
        else:
            print("Opzione non valida\n")


def fetch_again(again: bool = False) -> Path | None:
    """
    REFRESH: riscarica il config dallo stesso URL usato l'ultima volta.
    Ritorna il Path del config aggiornato, oppure None se non disponibile/errore.
    """
    global last_url
    if not last_url:
        print("⚠️ Nessun URL precedente: usa l'opzione [2] almeno una volta.")
        return None

    try:
        print(f"🔁 Refresh da: {last_url}")
        return _download_to_config(last_url)
    except Exception as e:
        print(f"❌ Errore durante il refresh")
        return None
