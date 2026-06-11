#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo per gestire il download del file config.yaml.
Compatibile con i percorsi e le logiche di PGS-X-FindIndex.
"""

from __future__ import annotations

import datetime
import logging
import random
from getpass import getpass
from pathlib import Path
import requests
import warnings as _warnings
from urllib3.exceptions import InsecureRequestWarning

from utils.exe.config import get_param, update_param
from utils.paths import get_config_path

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


def _build_base_url(addr: str) -> str:
    """
    Ritorna la base URL del PLC, senza path applicativi.
    Accetta indirizzi semplici, URL di download, URL Portal o URL FormLogin.
    """
    addr = addr.strip()
    if not addr:
        raise ValueError("Indirizzo PLC non valido")

    if "://" not in addr:
        addr = f"https://{addr}"

    addr = addr.rstrip("/")
    for marker in ("/UserFiles", "/Portal", "/FormLogin"):
        if marker in addr:
            addr = addr.split(marker, 1)[0]
            break

    return addr.rstrip("/")


def _get_plc_user_files_referer(base_url: str) -> str:
    """Referer usato dalla pagina UserFiles del PLC."""
    return f"{base_url}/Portal/Portal.mwsl?PriNav=UserFiles"


def _get_plc_headers(base_url: str) -> dict[str, str]:
    """Header minimi richiesti dalle azioni UserFiles/FormLogin."""
    return {
        "Origin": base_url,
        "Referer": _get_plc_user_files_referer(base_url),
    }


def _get_plc_error(session: requests.Session) -> tuple[str | None, str]:
    """
    Traduce l'eventuale cookie di errore UserFiles Siemens.
    Ritorna sempre una tupla per evitare errori in unpack.
    """
    plc_upload_codes = {
        "1": "Errore nel download del file",
        "2": "Operazione su file non consentita",
        "3": "Operazione file non consentita - nessun referente",
        "4": "Eliminazione fallita - memoria protetta da scrittura",
        "5": "Errore durante eliminazione file",
        "6": "Errore upload file (generico)",
        "7": "File già esistente",
        "8": "Memoria protetta da scrittura",
        "9": "Memoria piena",
        "10": "Caratteri non validi nel nome file",
        "11": "File troppo grande",
        "12": "Errore upload generico",
    }
    err = session.cookies.get("siemens_automation_user_files_error")
    if not err or err == "0":
        return None, "0"
    return plc_upload_codes.get(err, f"Unknown error code: {err}"), err


def login_plc(
    session: requests.Session,
    base_url: str,
    login: str = "config",
    password: str = "84210",
) -> bool:
    """
    Effettua il login sul PLC usando lo stesso flusso visto dal browser:

        POST {base_url}/FormLogin
        Payload: Redirection=&Login=config&Password=84210
        Referer: {base_url}/Portal/Portal.mwsl?PriNav=UserFiles
        Origin:  {base_url}

    Il PLC risponde normalmente con 302 Object Moved: viene considerato login OK.
    """
    base_url = _build_base_url(base_url)
    referer_url = _get_plc_user_files_referer(base_url)
    login_url = f"{base_url}/FormLogin"

    headers = _get_plc_headers(base_url)
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    payload = {
        "Redirection": "",
        "Login": login,
        "Password": password,
    }

    logging.info(f"🔐 Login PLC: {login_url}")

    # Prima apre la pagina UserFiles per inizializzare eventuali cookie di sessione.
    r = session.get(referer_url, verify=False, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Impossibile raggiungere il PLC: HTTP {r.status_code}")

    r = session.post(
        login_url,
        headers=headers,
        data=payload,
        verify=False,
        timeout=60,
        allow_redirects=False,
    )

    # Il browser mostra 302 Object Moved dopo il login: è il caso atteso.
    if r.status_code in (301, 302, 303, 307, 308):
        logging.info("✅ Login PLC effettuato")
        return True

    if 200 <= r.status_code < 300:
        logging.info("✅ Login PLC effettuato")
        return True

    raise RuntimeError(f"Login PLC fallito: HTTP {r.status_code}")


def _prompt_plc_login(session: requests.Session, base_url: str) -> bool:
    """Chiede le credenziali e chiama login_plc()."""
    login = input("Login PLC [config]: ").strip() or "config"
    password = getpass("Password PLC [84210]: ").strip() or "84210"
    return login_plc(session, base_url, login=login, password=password)


def download_file(url: str, dest_path: Path) -> None:
    """
    Scarica il file da un URL e lo salva in dest_path.
    Se HTTPS fallisce, prova HTTP in fallback.
    """
    logging.info("🌐 Download in corso...")
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

    logging.info(f"✅ File salvato in: {dest_path}")


def _get_next_config_backup_path(cfg_path: Path) -> Path:
    """
    Ritorna il prossimo path di backup disponibile:

        config_old_1.yaml
        config_old_2.yaml
        config_old_3.yaml
        ...

    Il numero viene calcolato leggendo i backup già presenti nella stessa
    cartella di config.yaml.
    """
    backup_dir = cfg_path.parent
    prefix = "config_old_"
    max_num = 0

    for path in backup_dir.glob(f"{prefix}*.yaml"):
        suffix = path.stem[len(prefix):]

        if suffix.isdigit():
            max_num = max(max_num, int(suffix))

    next_num = max_num + 1
    backup_path = backup_dir / f"{prefix}{next_num}.yaml"

    # Sicurezza extra: evita sovrascritture se per qualche motivo il file esiste già
    while backup_path.exists():
        next_num += 1
        backup_path = backup_dir / f"{prefix}{next_num}.yaml"

    return backup_path


def _download_to_config(url: str) -> Path:
    """
    Scarica il file come config_temp.yaml.

    Se config.yaml esiste già, viene confrontato con config_temp.yaml.
    Il backup viene creato solo se i due file sono diversi.

    Backup:
        config_old_1.yaml
        config_old_2.yaml
        config_old_3.yaml
        ...

    Se il file scaricato è identico al config attuale, config.yaml non viene
    modificato e config_temp.yaml viene eliminato.
    """
    cfg_path = get_config_path("config.yaml", prefer_cwd=True)
    temp_path = cfg_path.with_name("config_temp.yaml")

    # --- Download nuovo file su config_temp.yaml ---
    download_file(url, temp_path)

    config_exists = cfg_path.exists()
    config_changed = True

    # --- Confronto con il config attuale ---
    if config_exists:
        try:
            config_changed = cfg_path.read_bytes() != temp_path.read_bytes()
        except Exception as e:
            logging.info(f"⚠️ Errore durante il confronto dei file: {e}")
            raise

    # --- Se non ci sono differenze, non fare backup e non sostituire ---
    if config_exists and not config_changed:
        logging.info(
            "✅ Il config scaricato è identico a quello attuale. "
            "Nessun backup necessario."
        )

        try:
            temp_path.unlink()
        except Exception as e:
            logging.info(f"⚠️ Impossibile eliminare config_temp.yaml: {e}")

        lastUrl = get_param("lastUrl")
        if lastUrl != url:
            update_param("lastUrl", url)

        return cfg_path

    # --- Backup del config attuale solo se diverso ---
    if config_exists and config_changed:
        backup_path = _get_next_config_backup_path(cfg_path)

        try:
            backup_path.write_bytes(cfg_path.read_bytes())
            logging.info(f"📦 Backup effettuato: {backup_path}")
        except Exception as e:
            logging.info(f"⚠️ Errore durante il backup: {e}")
            raise

    # --- Sostituzione config.yaml con config_temp.yaml ---
    try:
        temp_path.replace(cfg_path)
        logging.info(f"✅ Config aggiornato: {cfg_path}")
    except Exception as e:
        logging.info(f"⚠️ Errore durante la sostituzione del config: {e}")
        raise

    lastUrl = get_param("lastUrl")
    if lastUrl != url:
        update_param("lastUrl", url)

    return cfg_path


def choose_and_prepare_config(sn: str = None, firstRun: bool = False) -> Path:
    """
    Chiede all'utente se usare il config locale o scaricarlo.
    Ritorna il percorso finale del file pronto.
    """
    lastUrl = get_param('lastUrl')
    cfg_path = get_config_path("config.yaml", prefer_cwd=True)
    plc_session: requests.Session | None = None
    plc_session_base_url: str | None = None

    while True:
        logging.info('')
        logging.info("Selezione sorgente file 'config.yaml'")
        logging.info("  [1] Usa file locale (cartella corrente)")
        logging.info("  [2] Scarica file da rete")
        if lastUrl:
            logging.info("  [3] Aggiorna file da rete (ultimo URL)")
        if sn:
            logging.info("  [4] Save")
        if lastUrl:
            logging.info("  [5] FORCE-UPLOAD [RISK]")
        logging.info("  [6] Login PLC")
        if firstRun and lastUrl and get_param("downloadOnStart"):
            logging.info("\n⚠️ Download automatico al primo avvio da config.json")
            choice = "3"
            firstRun = False
        else:
            choice = input("Scelta: ").strip()

        if choice == "2":
            base = input("Inserisci indirizzo/IP (es: 10.3.73.177): ").strip()
            if not base:
                logging.info("Indirizzo non valido.\n")
                continue

            url = _build_download_url(base)
            try:
                return _download_to_config(url)
            except Exception:
                logging.info("❌ Errore nel download")
                continue

        elif choice == "1":
            if cfg_path.exists():
                return cfg_path
            logging.info(f"❌ File locale non trovato o corrotto: {cfg_path}\n")
            continue
        elif choice == "3" and lastUrl:
            res = fetch_again()
            if res is not None:
                return res
        elif choice == "4" and sn:
            if not cfg_path.exists():
                logging.info(f"❌ File locale non trovato o corrotto: {cfg_path}\n")
            ver = input("Versione progetto: ")
            save_version(sn=sn, ver=ver, date=str(datetime.datetime.now().strftime("%Y%m%d")))
            return cfg_path
        elif choice == "5" and lastUrl:
            """
            TODO:
            prima cancello il file con (devo mandare anche gli header della pagina da cui arrivos e no non va)
            https://192.168.1.250/UserFiles?Action=DELETE&Name=config.yaml
            poi carico il nuovo file config.yaml con (devo mandare anche gli header della pagina da cui arrivos e no non va)
            https://192.168.1.250/UserFiles?Action=UPLOAD
            """
            try:
                cfg_path = get_config_path("config.yaml", prefer_cwd=True)

                if not cfg_path.exists():
                    logging.info(f"❌ File locale non trovato: {cfg_path}")
                    continue
                pin = ''.join(str(random.randint(0, 9)) for _ in range(4))

                if input(f'Sicuro? [{pin}]') != pin:
                    continue

                base_url = _build_base_url(lastUrl)
                referer_url = _get_plc_user_files_referer(base_url)
                delete_url = f"{base_url}/UserFiles?Action=DELETE&Name=config.yaml"
                upload_url = f"{base_url}/UserFiles?Action=UPLOAD"

                if plc_session is None or plc_session_base_url != base_url:
                    logging.info("🌐 Apertura sessione...")
                    plc_session = requests.Session()
                    plc_session_base_url = base_url
                    _prompt_plc_login(plc_session, base_url)

                session = plc_session
                headers = _get_plc_headers(base_url)

                # -------------------------------------------------
                # STEP 1 - DELETE vecchio file
                # -------------------------------------------------
                logging.info("🗑️ Eliminazione vecchio config.yaml...")
                r = session.get(referer_url, verify=False, timeout=60)
                if r.status_code != 200:
                    logging.info(f"❌ Errore FORCE-UPLOAD: Impossibile raggiungere il PLC {r.status_code}")
                    continue

                r = session.post(delete_url, headers=headers, verify=False, timeout=60)

                if r.status_code != 200:
                    logging.info(f"❌ Errore FORCE-UPLOAD: Impossibile cancellare il config {r.status_code}")
                    continue

                msg, code = _get_plc_error(session)
                if msg and code != "0":
                    logging.warning(f"❌ PLC ERROR: {msg}")
                else:
                    logging.info("✅ Vecchio config eliminato")

                # -------------------------------------------------
                # STEP 2 - UPLOAD nuovo file
                # -------------------------------------------------
                logging.info("⬆️ Upload nuovo config.yaml...")

                with open(cfg_path, 'rb') as fh:
                    files = {
                        'File': ('config.yaml', fh, 'application/octet-stream')
                    }

                    r = session.post(
                        upload_url,
                        headers=headers,
                        files=files,
                        verify=False,
                        timeout=60
                    )

                r.raise_for_status()

                msg, code = _get_plc_error(session)

                if msg and code != "0":
                    logging.warning(f"❌ PLC ERROR: {msg}")
                else:
                    logging.info("✅ Upload completato")

                return cfg_path

            except Exception as e:
                logging.info(f"❌ Errore FORCE-UPLOAD: {e}")
                continue
        elif choice == "6":
            try:
                if lastUrl:
                    default_base_url = _build_base_url(lastUrl)
                    base = input(f"Indirizzo/IP PLC [{default_base_url}]: ").strip() or default_base_url
                else:
                    base = input("Indirizzo/IP PLC (es: 10.3.253.1): ").strip()

                if not base:
                    logging.info("Indirizzo non valido.\n")
                    continue

                base_url = _build_base_url(base)
                plc_session = requests.Session()
                plc_session_base_url = base_url
                result = _prompt_plc_login(plc_session, base_url)

                print('OK' + str(result))
            except Exception as e:
                plc_session = None
                plc_session_base_url = None
                logging.info(f"❌ Errore login PLC: {e}")
                continue
        else:
            logging.info("Opzione non valida\n")


def fetch_again(again: bool = False) -> Path | None:
    """
    REFRESH: riscarica il config dallo stesso URL usato l'ultima volta.
    Ritorna il Path del config aggiornato, oppure None se non disponibile/errore.
    """
    lastUrl = get_param("lastUrl")
    if not lastUrl:
        logging.info("⚠️ Nessun URL precedente: usa l'opzione [2] almeno una volta.")
        return None

    try:
        logging.info(f"🔁 Refresh da: {lastUrl}")
        return _download_to_config(lastUrl)
    except Exception as e:
        logging.info(f"❌ Errore durante il refresh")
        return None


def save_version(sn: str, ver:str, date: str) -> bool:
    cfg_path = get_config_path("config.yaml", prefer_cwd=True)
    backup_path = cfg_path.with_name(f"config {sn} {ver} {date}.yaml")

    # --- Backup automatico ---
    if cfg_path.exists():
        try:
            # se esiste config_old.yaml, sovrascrivi
            backup_path.write_bytes(cfg_path.read_bytes())
            logging.info(f"📦 Backup effettuato: {backup_path}")
            return True
        except Exception as e:
            logging.info(f"⚠️ Errore durante il salvataggio: {e}")
            return False


if __name__ == "__main__":
    choose_and_prepare_config()