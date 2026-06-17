#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo per gestire il download del file config.yaml.
Compatibile con i percorsi e le logiche di PGS-X-FindIndex.
"""

from __future__ import annotations

import datetime
import html
import logging
import random
import re
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


def _get_plc_headers(base_url: str, files: bool = False, returnURL: bool = False) -> dict[str, str] | str:
    """Header minimi richiesti dalle azioni UserFiles/FormLogin."""
    url = f"{base_url}/Portal/Portal.mwsl?PriNav=Start"
    if files:
        url = f"{base_url}/Portal/Portal.mwsl?PriNav=UserFiles"

    if not returnURL:
        return {
            "Origin": base_url,
            "Referer": url,
        }
    else:
        return url


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


def _stop_cpu(plc_session: requests.Session, base_url: str) -> bool:
    """Invia comando per fermare la CPU del PLC."""
    url = f"{base_url}/ClientArea/CPUAction.mwsl?Action=Stop"
    headers = _get_plc_headers(base_url)
    r = plc_session.get(url, headers=headers, verify=False, timeout=20)
    return r.status_code == 200


def _start_cpu(plc_session: requests.Session, base_url: str) -> bool:
    """Invia comando per avviare la CPU del PLC."""
    url = f"{base_url}/ClientArea/CPUAction.mwsl?Action=Start"
    headers = _get_plc_headers(base_url)
    r = plc_session.get(url, headers=headers, verify=False, timeout=20)
    return r.status_code == 200


def _get_cpu_run_status(plc_session: requests.Session, base_url: str) -> str:
    """
       Estrae il nome progetto dalla pagina Start del PLC.

       Esempio:
           <td id="startpage_operatingmode_value" class="output_field_long">
               RUN
           </td>
       """
    url = f"{base_url}/Portal/Portal.mwsl?PriNav=Start"
    r = plc_session.get(url, verify=False, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Impossibile leggere pagina Start PLC: HTTP {r.status_code}")

    match = re.search(
        "<td\\b(?=[^>]*\\bid=[\"\']startpage_operatingmode_value[\"\'])[^>]*>(.*?)</td>",
        r.text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        raise RuntimeError("Stato CPU PLC non trovato nella pagina Start")

    value = re.sub(r"<[^>]+>", "", match.group(1))
    return html.unescape(value).strip()


def _get_plc_start_url(base_url: str) -> str:
    """URL della pagina Start del PLC, usata per leggere il nome progetto."""
    return f"{base_url}/Portal/Portal.mwsl?PriNav=Start"


def _extract_plc_project_name(start_page_html: str) -> str:
    """
    Estrae il nome progetto dalla pagina Start del PLC.

    Esempio:
        <td id="startpage_projectname_value" class="output_field_long">
            PGSX - 0.25.50.6.6820_1510SNew
        </td>
    """
    match = re.search(
        "<td\\b(?=[^>]*\\bid=[\"\']startpage_projectname_value[\"\'])[^>]*>(.*?)</td>",
        start_page_html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        raise RuntimeError("Nome progetto PLC non trovato nella pagina Start")

    value = re.sub(r"<[^>]+>", "", match.group(1))
    return html.unescape(value).strip()


def _extract_commessa_from_project_name(project_name: str) -> str:
    """
    Estrae la commessa dal nome progetto PLC.

    Esempi:
        PGSX - 0.25.50.6.6820_1510SNew -> 6820
        PGSX - 0.25.50.6.6820_1510New  -> 6820
        PGSX - 0.25.50.6.6820_1520     -> 6820

    Regola:
        prende il numero completo subito prima di _15xx...
    """
    match = re.search(r"\.(\d+)_15\d+", project_name)

    if not match:
        raise RuntimeError(
            f"Commessa non trovata nel nome progetto PLC: {project_name!r}"
        )

    return match.group(1)


def _ribalta_commessa(commessa: str) -> str:
    """
    Applica il complemento a 10 su ogni cifra della commessa.

    Regola:
        0 -> 0
        1 -> 9
        2 -> 8
        3 -> 7
        4 -> 6
        5 -> 5
        6 -> 4
        7 -> 3
        8 -> 2
        9 -> 1

    Esempi:
        6820 -> 4280
        1507 -> 9503
        1234 -> 9876
    """
    if not commessa.isdigit():
        raise ValueError(f"Commessa non numerica: {commessa!r}")

    return "".join(str((10 - int(cifra)) % 10) for cifra in commessa)


def _build_password_from_commessa(commessa: str) -> str:
    """Costruisce la password dinamica PLC dalla commessa."""
    commessa_ribaltata = _ribalta_commessa(commessa)
    return f"{commessa_ribaltata}codicePLC"


def _response_has_cookie(response: requests.Response, cookie_name: str) -> bool:
    """
    Controlla se il cookie esiste nella response o in una response precedente
    in caso di redirect seguito automaticamente da requests.
    """
    responses = list(response.history or []) + [response]

    for resp in responses:
        for cookie in resp.cookies:
            if cookie.name == cookie_name and cookie.value:
                return True

    return False


def _session_has_cookie(plc_session: requests.Session, cookie_name: str) -> bool:
    """
    Controlla se il cookie esiste nella sessione requests corrente.

    Utile dopo un login PLC per verificare, ad esempio, la presenza di:
        siemens_ad_session
    """
    if plc_session is None or not hasattr(plc_session, "cookies"):
        return False

    for cookie in plc_session.cookies:
        if cookie.name == cookie_name and cookie.value:
            return True

    return False


def _is_login_ok(response: requests.Response) -> bool:
    """
    Valuta se il login PLC e' andato a buon fine.

    Il caso Siemens piu' affidabile e' la presenza del cookie:
        siemens_ad_session

    Nota:
    se requests segue automaticamente il redirect, il 302 puo' trovarsi
    in response.history, mentre response.status_code puo' essere 200.
    """

    # Caso migliore: login riuscito se esiste il cookie di sessione Siemens
    if _response_has_cookie(response, "siemens_ad_session"):
        return True

    # Se il PLC restituisce un redirect dopo login, puo' essere OK
    # if response.status_code in (301, 302, 303, 307, 308):
    #     return True

    # Se requests ha seguito il redirect automaticamente
    # if any(r.status_code in (301, 302, 303, 307, 308) for r in response.history or []):
    #     return True

    # Qualsiasi errore HTTP non e' login OK
    if not 200 <= response.status_code < 300:
        return False

    # Su 2xx controlla che non sia stata ripresentata la pagina di login
    # body_lower = (response.text or "").lower()
    #
    # login_form_markers = (
    #     'name="login"',
    #     "name='login'",
    #     'name="password"',
    #     "name='password'",
    #     "/formlogin",
    #     "formlogin",
    # )
    #
    # return not any(marker in body_lower for marker in login_form_markers)
    return False


def _login_plc_with_credentials(
    session: requests.Session,
    base_url: str,
    login: str,
    password: str,
) -> requests.Response:
    """Esegue un singolo tentativo di login con le credenziali indicate."""
    base_url = _build_base_url(base_url)
    referer_url = _get_plc_headers(base_url=base_url, returnURL=True)
    login_url = f"{base_url}/FormLogin"

    headers = _get_plc_headers(base_url)
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    payload = {
        "Redirection": "",
        "Login": login,
        "Password": password,
    }

    # Prima apre la pagina UserFiles per inizializzare eventuali cookie di sessione.
    r = session.get(referer_url, verify=False, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Impossibile raggiungere il PLC: HTTP {r.status_code}")

    return session.post(
        login_url,
        headers=headers,
        data=payload,
        verify=False,
        timeout=60,
        allow_redirects=False,
    )


def _get_plc_commessa_from_start_page(
    session: requests.Session,
    base_url: str,
) -> str:
    """Carica la pagina Start del PLC, legge il nome progetto ed estrae la commessa."""
    base_url = _build_base_url(base_url)
    start_url = _get_plc_start_url(base_url)

    logging.info(f"📄 Lettura pagina Start PLC: {start_url}")

    r = session.get(start_url, verify=False, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(
            f"Impossibile leggere pagina Start PLC: HTTP {r.status_code}"
        )

    project_name = _extract_plc_project_name(r.text)
    commessa = _extract_commessa_from_project_name(project_name)

    logging.info(f"📌 Nome progetto PLC: {project_name}")
    logging.info(f"📌 Commessa PLC estratta: {commessa}")

    return commessa


def login_plc(
    plc_session: requests.Session,
    base_url: str,
    login: str = "config",
    password: str = "84210",
) -> bool:
    """
    Effettua il login sul PLC.

    Primo tentativo:
        username: config
        password: 84210

    Se il primo tentativo fallisce:
        1. carica:
           {base_url}/Portal/Portal.mwsl?PriNav=Start

        2. legge il campo:
           <td id="startpage_projectname_value">...</td>

        3. estrae la commessa dal nome progetto:
           PGSX - 0.25.50.6.6820_1510SNew -> 6820

        4. calcola la password:
           6820 -> 4280
           password -> 4280codicePLC

        5. ritenta il login con:
           username: config
           password: {commessa_ribaltata}codicePLC
    """
    base_url = _build_base_url(base_url)
    login_url = f"{base_url}/FormLogin"

    logging.info(f"🔐 Login PLC: {login_url}")

    r = _login_plc_with_credentials(
        session=plc_session,
        base_url=base_url,
        login=login,
        password=password,
    )
    if _is_login_ok(r):
        logging.info("✅ Login PLC effettuato")
        return True

    logging.warning(f"⚠️ Primo login PLC fallito: HTTP {r.status_code}")

    commessa = _get_plc_commessa_from_start_page(
        session=plc_session,
        base_url=base_url,
    )
    dynamic_password = _build_password_from_commessa(commessa)

    logging.info("🔐 Ritento login PLC con password dinamica da commessa")
    logging.info(f"📌 Commessa ribaltata: {_ribalta_commessa(commessa)}")

    r = _login_plc_with_credentials(
        session=plc_session,
        base_url=base_url,
        login="config",
        password=dynamic_password,
    )

    if _is_login_ok(r):
        logging.info("✅ Login PLC effettuato con password dinamica")
        return True

    raise RuntimeError(
        f"Login PLC fallito anche con password dinamica: HTTP {r.status_code}"
    )


def download_file(plc_session: requests.Session, url: str, dest_path: Path) -> None:
    """
    Scarica il file da un URL e lo salva in dest_path.
    Se HTTPS fallisce, prova HTTP in fallback.
    """
    logging.info("🌐 Download in corso...")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        r = plc_session.get(url, timeout=60, verify=False)
        r.raise_for_status()
        dest_path.write_bytes(r.content)
    except Exception as e_https:
        # Fallback HTTP
        try:
            if url.startswith("https://"):
                url_http = "http://" + url[len("https://"):]
                r = plc_session.get(url_http, timeout=60)
                r.raise_for_status()
                dest_path.write_bytes(r.content)
            else:
                raise
        except Exception as e_http:
            raise RuntimeError(f"Errore nel download:\nHTTPS: {e_https}\nHTTP: {e_http}") from e_http

    logging.info(f"✅ File salvato in: {dest_path}")


def is_valid_download(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False

    text = path.read_text(encoding="utf-8", errors="ignore").strip()

    if not text:
        return False

    bad_markers = (
        "<html",
        "<!doctype html",
        "formlogin",
        "login",
        "password",
    )

    text_lower = text.lower()
    if any(marker in text_lower for marker in bad_markers):
        return False

    return True


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


def _download_to_config(plc_session: requests.Session, url: str) -> Path:
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
    download_file(plc_session=plc_session, url=url, dest_path=temp_path)

    if is_valid_download(temp_path):
        logging.info("✅ Download valido")
    else:
        # todo:  RIPROVO LOGIN e riprovo a scaricare
        if get_param("loginEnabled"):
            login_plc(plc_session=plc_session, base_url=_build_base_url(url))
            download_file(plc_session=plc_session, url=url, dest_path=temp_path)
            if is_valid_download(temp_path):
                logging.info("✅ Download valido")
            else:
                raise RuntimeError("Il file scaricato non è valido")
        else:
            raise RuntimeError("Il file scaricato non è valido")

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
    plc_session = requests.Session()
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
            if get_param("loginEnabled") and not _session_has_cookie(plc_session=plc_session, cookie_name="siemens_ad_session"):
                login_to_plc(plc_session=plc_session, host=base)
            url = _build_download_url(base)
            try:
                return _download_to_config(plc_session=plc_session, url=url)
            except Exception:
                logging.info("❌ Errore nel download")
                continue

        elif choice == "1":
            if cfg_path.exists():
                return cfg_path
            logging.info(f"❌ File locale non trovato o corrotto: {cfg_path}\n")
            continue
        elif choice == "3" and lastUrl:
            res = fetch_again(plc_session=plc_session)
            if res is not None:
                return res
        elif choice == "4" and sn:
            if not cfg_path.exists():
                logging.info(f"❌ File locale non trovato o corrotto: {cfg_path}\n")
                continue
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
                referer_url = _get_plc_headers(base_url=base_url, files=True, returnURL=True)
                delete_url = f"{base_url}/UserFiles?Action=DELETE&Name=config.yaml"
                upload_url = f"{base_url}/UserFiles?Action=UPLOAD"
                # todo verificare se la sessione è già aperta e se è per lo stesso PLC, altrimenti aprirla e fare login
                if plc_session is None or plc_session_base_url != base_url:
                    logging.info("🌐 Apertura sessione...")
                    plc_session = requests.Session()
                    plc_session_base_url = base_url
                    login_plc(plc_session, base_url)

                session = plc_session
                headers = _get_plc_headers(base_url, files=True)

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
                    continue
                else:
                    logging.info("✅ Upload completato")

                _cpu_status = _get_cpu_run_status(plc_session=plc_session, base_url=base_url)
                if _cpu_status == "RUN" or _cpu_status == "AVVIAMENTO":
                    if _stop_cpu(plc_session=plc_session, base_url=base_url):
                        logging.info("✅ CPU fermata")
                    else:
                        logging.info("❌ Errore nel fermare CPU")
                if _start_cpu(plc_session=plc_session, base_url=base_url):
                    logging.info("✅ CPU avviata")
                else:
                    logging.info("❌ Errore durante l'avvio CPU")
                return cfg_path

            except Exception as e:
                logging.info(f"❌ Errore FORCE-UPLOAD: {e}")
                continue
        else:
            logging.info("Opzione non valida\n")


def login_to_plc(plc_session: requests.Session, host: str = None, lastUrl: str = None):
    try:
        if lastUrl:
            host = _build_base_url(lastUrl)f

        if not host:
            logging.info("Indirizzo non valido.\n")
            return

        base_url = _build_base_url(host)
        # TODO: need login?
        login_plc(plc_session, base_url)
    except Exception as e:
        logging.info(f"❌ Errore login PLC: {e}")


def fetch_again(plc_session: requests.Session) -> Path | None:
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
        if get_param("loginEnabled"):
            login_to_plc(plc_session=plc_session, lastUrl=lastUrl)
        return _download_to_config(plc_session=plc_session, url=lastUrl)
    except Exception as e:
        logging.info(f"❌ Errore durante il refresh")
        return None


def save_version(sn: str, ver: str, date: str) -> bool:
    cfg_path = get_config_path("config.yaml", prefer_cwd=True)

    save_folder = get_param("defaultSaveFolder")

    backup_dir = cfg_path.parent / save_folder

    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / f"config {sn} {ver} {date}.yaml"

    # --- Backup automatico ---
    if cfg_path.exists():
        try:
            backup_path.write_bytes(cfg_path.read_bytes())
            logging.info(f"📦 Backup effettuato: {backup_path}")
            return True
        except Exception as e:
            logging.exception(f"⚠️ Errore durante il salvataggio: {e}")
            return False

    logging.warning(f"⚠️ File config non trovato: {cfg_path}")
    return False


if __name__ == "__main__":
    choose_and_prepare_config()