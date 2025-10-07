#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo per gestire il download del file config.yaml.
Compatibile con i percorsi e le logiche di PSG-X-FindIndex.
"""

from __future__ import annotations
from pathlib import Path
import requests
import yaml
import warnings as _warnings
from urllib3.exceptions import InsecureRequestWarning

from utils.path import get_config_path

_warnings.simplefilter("ignore", InsecureRequestWarning)


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


def choose_and_prepare_config() -> Path:
    """
    Chiede all'utente se usare il config locale o scaricarlo.
    Ritorna il percorso finale del file pronto.
    """
    cfg_path = get_config_path("config.yaml", prefer_cwd=True)

    while True:
        print("\nSelezione sorgente file 'config.yaml'")
        print("  [1] Usa file locale (cartella corrente)")
        print("  [2] Scarica da rete (connessione non protetta)")
        choice = input("Scelta: ").strip()

        if choice == "2":
            base = input("Inserisci indirizzo/IP (es: 10.3.73.177): ").strip()
            if not base:
                print("Indirizzo non valido.\n")
                continue

            url = _build_download_url(base)
            dest = cfg_path
            try:
                download_file(url, dest)
                return dest
            except Exception as e:
                print(f"Errore nel download: {e}\n")
                continue

        elif choice == "1":
            if cfg_path.exists():
                return cfg_path
            print(f"❌ File locale non trovato o corrotto: {cfg_path}\n")
            continue

        else:
            print("Opzione non valida\n")


def fetch_again(again=False):

    # TODO: reintegrare il REFRESH
    ...
    # if tipo == "0":
    #     if last_url:
    #         print("Riscarico config da internet...")
    #         try:
    #             r = requests.get(last_url, verify=False, timeout=10)
    #             r.raise_for_status()
    #             path = get_run_dir() / "config.yaml"
    #             path.write_text(r.text, encoding="utf-8")
    #             data = load_yaml(str(path))
    #             print("Config riscaricato con successo.")
    #         except Exception as e:
    #             print(f"Errore durante il refresh: {e}")
    #     else:
    #         print("Nessun URL precedente: devi prima scegliere l'opzione 2 per scaricare.")
    #     continue
