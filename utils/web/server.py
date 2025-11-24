#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/web/server.py

Mini web layer per PGS-X-F:
espone via HTTP le stesse ricerche che prima facevi da console (main.py).

Non tocca la logica di calcolo / parsing:
riusa direttamente utils.db.data_config, utils.yaml.*, ecc.
"""

from __future__ import annotations

import logging
import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flask import Flask, jsonify, request

from utils.exe.config import load_exe_config
from utils.version import get_version_info
from utils.db import data_config  # <- oggetto DATA_CONFIG
from utils.db.data_config import (
    populate_from_yaml_file,
    run_io_search,
    IO_DI,
    IO_AI,
    IO_DO,
    IO_AO,
    IO_RI,
    decode_sys_addr,
    custom_function,
)
from utils.yaml.data.core import make_axis_sys_addr, make_alarm_sys_addr
from utils.exports.tia_constants import HEADER_SN
import utils.yaml.download as yaml_download
from utils.yaml.download import (
    _build_download_url,
    _download_to_config,
    fetch_again,
    save_version,
)

INDEX_HTML = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <title>PGS-X-F – Web CLI</title>
  <style>
    :root {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color-scheme: dark;
    }
    body {
      margin: 0;
      background: #020617;
      color: #e5e7eb;
      min-height: 100vh;
    }
    #app {
      width: 100%;
      height: 100vh;
      margin: 0;
      border-radius: 0;
      border: none;
      background: #020617;
      display: flex;
      flex-direction: column;
    }
    .console {
      padding: 0.9rem 1.1rem;
      font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.8rem;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
      flex: 1;
    }
    .console-line {
      line-height: 1.45;
    }
    .console-line.system { color: #9ca3af; }
    .console-line.ok { color: #22c55e; }
    .console-line.error { color: #f97373; }
    .console-line.cmd { color: #e5e7eb; }
    .prompt {
      color: #4ade80;
    }
    .status-bar {
      border-top: 1px solid #111827;
      padding: 0.25rem 1.1rem;
      font-size: 0.7rem;
      color: #6b7280;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(15,23,42,0.85);
    }
    .cmd-bar {
      border-top: 1px solid #111827;
      padding: 0.45rem 1.1rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      background: rgba(15,23,42,0.95);
    }
    .cmd-bar span {
      font-family: "JetBrains Mono", ui-monospace;
      font-size: 0.8rem;
      color: #4ade80;
    }
    .cmd-input {
      flex: 1;
      background: #020617;
      border-radius: 999px;
      border: 1px solid #1f2937;
      padding: 0.35rem 0.7rem;
      font-size: 0.8rem;
      color: #e5e7eb;
      outline: none;
    }
    .cmd-input:focus {
      border-color: #22c55e;
      box-shadow: 0 0 0 1px rgba(34,197,94,0.35);
    }
  </style>
</head>
<body>
<div id="app">
  <div class="console" id="console"></div>
  <div class="status-bar">
    <span id="status-left">PGS-X-F Web CLI</span>
    <span id="status-right">config: sconosciuto · versione: n/d</span>
  </div>
  <form class="cmd-bar" id="cmd-form">
    <span>&gt;</span>
    <input id="cmd-input" class="cmd-input" autocomplete="off" placeholder="digita qui e premi Invio..." />
  </form>
</div>

<script>
  const consoleEl = document.getElementById('console');
  const statusLeft = document.getElementById('status-left');
  const statusRight = document.getElementById('status-right');
  const form = document.getElementById('cmd-form');
  const input = document.getElementById('cmd-input');

  let state = 'WAIT_CONFIG_MODE';
  let ctx = {};
  let hasLastUrl = false;
  let snAvailable = false;

  function appendLine(text, klass) {
    const line = document.createElement('div');
    line.className = 'console-line ' + (klass || '');
    line.innerHTML = '<span class="prompt">&gt;&nbsp;</span>' + text;
    consoleEl.appendChild(line);
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }

  function appendRaw(text, klass) {
    const line = document.createElement('div');
    line.className = 'console-line ' + (klass || '');
    line.textContent = text;
    consoleEl.appendChild(line);
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }

  function pretty(obj) {
    try { return JSON.stringify(obj, null, 2); }
    catch (e) { return String(obj); }
  }

  async function callApi(method, url, body) {
    appendLine(method + ' ' + url, 'cmd');
    const opts = { method, headers: {} };
    if (body) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    try {
      const res = await fetch(url, opts);
      const data = await res.json();
      if (!res.ok || data.ok === false) {
        appendRaw(pretty(data), 'error');
      } else {
        appendRaw(pretty(data), 'ok');
      }
      return data;
    } catch (err) {
      appendRaw('Errore di rete: ' + err, 'error');
      throw err;
    }
  }

    async function refreshStatus() {
      try {
        const data = await callApi('GET', '/api/status');
        let cfg = 'non caricato';
        if (data && data.config_loaded) {
          cfg = 'caricato';
          if (data.config_path) cfg += ' (' + data.config_path + ')';
        }
        const ver = data && data.version ? data.version : 'n/d';
        statusRight.textContent = 'config: ' + cfg + ' · versione: ' + ver;
    
        snAvailable = !!(
          data &&
          data.config_loaded &&
          data.sn !== null &&
          data.sn !== -1
        );
        hasLastUrl = !!(data && data.has_last_url);
    
        if (snAvailable) {
          statusLeft.textContent = 'PGS-X-F Web CLI · SN: ' + data.sn;
        } else {
          statusLeft.textContent = 'PGS-X-F Web CLI';
        }
      } catch (e) {
        // già loggato in console
      }
    }


function printConfigQuestion() {
  const lines = [
    '',
    "Selezione sorgente file 'config.yaml'",
    "  [1] Usa file locale (cartella corrente)",
    "  [2] Scarica file da rete",
  ];

  if (hasLastUrl) {
    lines.push("  [3] Aggiorna file da rete (ultimo URL)");
  }
  if (snAvailable) {
    lines.push("  [4] Save (backup versionato per SN corrente)");
  }

  lines.push('');
  lines.push('Scelta (1-4):');
  lines.push('');

  appendRaw(lines.join('\\n'), 'system');
}


  function printMenu() {
    appendRaw(
      [
        '',
        '=== MENU PRINCIPALE ===',
        '1) Ricerca IO (menu 1..4) -> chiede tipo IO + indice',
        '5) SYSTEM (AXIS/ALARM)',
        '6) CHECK custom_function()',
        '7) FREE scan',
        '8) Esci / reset menu',
        '',
        'Comandi extra: status | config | config <percorso>',
        ''
      ].join('\\n'),
      'system'
    );
  }

  function resetFlow() {
    ctx = {};
    state = 'WAIT_MAIN_CHOICE';
    printMenu();
  }

async function handleEnter(rawCmd) {
  const cmd = (rawCmd || '').trim();

  // Comportamento "Invio" come nel CLI:
  // - se siamo nel menu principale e premi Invio vuoto -> riapre la scelta config
  if (!cmd) {
    if (state === 'WAIT_MAIN_CHOICE') {
      appendRaw('', 'system');
      state = 'WAIT_CONFIG_MODE';
      printConfigQuestion();
    }
    return;
  }

  appendLine(cmd, 'cmd');

  switch (state) {
    // --- Fase CONFIG: replica choose_and_prepare_config() ---
    case 'WAIT_CONFIG_MODE': {
        if (cmd === '1' || cmd.toLowerCase() === 'l') {
          appendRaw('Uso config locale (config.yaml / PGS_CONFIG_PATH)...', 'system');
          let res;
          try {
            res = await callApi('POST', '/api/config/load', {});
          } catch (e) {
            // errore di rete: resta nella scelta config
            appendRaw('Errore di rete nel caricamento del config.', 'error');
            printConfigQuestion();
            break;
          }
          await refreshStatus();

          if (!res || res.ok === false) {
            // file mancante o parsing fallito -> stessa domanda di nuovo
            appendRaw('Config non caricato. Controlla il file/percorso e riprova.', 'error');
            state = 'WAIT_CONFIG_MODE';
            printConfigQuestion();
          } else {
            // solo se è andato bene vado al menu
            state = 'WAIT_MAIN_CHOICE';
            printMenu();
          }

        } else if (cmd === '2' || cmd.toLowerCase() === 'r') {
          state = 'WAIT_REMOTE_IP';
          appendRaw('Inserisci indirizzo IP del server config (es. 10.0.0.10):', 'system');

        } else {
          appendRaw('Scelta non valida. Usa 1 (locale) o 2 (rete).', 'error');
          printConfigQuestion();
        }
        break;
      }

    case 'WAIT_SAVE_VERSION': {
      if (!cmd) {
        appendRaw('Versione vuota, riprova.', 'error');
        appendRaw('Versione progetto:', 'system');
        break;
      }
      appendRaw('Salvo versione ' + cmd + '...', 'system');
      await callApi('POST', '/api/config/prepare', {
        mode: 'save',
        version: cmd,
      });
      await refreshStatus();
      state = 'WAIT_MAIN_CHOICE';
      printMenu();
      break;
    }

      case 'WAIT_REMOTE_IP': {
        if (!cmd) {
          appendRaw('IP vuoto, riprova.', 'error');
          appendRaw('Inserisci indirizzo IP del server config (es. 10.0.0.10):', 'system');
          break;
        }
        ctx.remoteIp = cmd;
        appendRaw('Scarico config da IP ' + ctx.remoteIp + '...', 'system');

        let res;
        try {
          res = await callApi('POST', '/api/config/prepare', {
            mode: 'remote',
            ip: ctx.remoteIp
          });
        } catch (e) {
          appendRaw('Errore di rete nel download del config.', 'error');
          state = 'WAIT_CONFIG_MODE';
          printConfigQuestion();
          break;
        }

        await refreshStatus();

        if (!res || res.ok === false) {
          appendRaw('Download/config da rete fallito. Controlla IP/URL e riprova.', 'error');
          state = 'WAIT_CONFIG_MODE';
          printConfigQuestion();
        } else {
          state = 'WAIT_MAIN_CHOICE';
          printMenu();
        }
        break;
      }


    // --- MENU principale: replica while True del CLI ---
    case 'WAIT_MAIN_CHOICE': {
      if (['1','2','3','4'].includes(cmd)) {
        ctx.menu = parseInt(cmd, 10);
        state = 'WAIT_IO_TYPE';
        appendRaw('Tipo IO? [DI/DO/AI/AO/RI]', 'system');

      } else if (cmd === '5') {
        state = 'WAIT_SYSTEM_KIND';
        appendRaw('SYSTEM kind? [AXIS/ALARM]', 'system');

      } else if (cmd === '6') {
        appendRaw('Eseguo CHECK custom_function()...', 'system');
        await callApi('GET', '/api/check');
        resetFlow();

      } else if (cmd === '7') {
        state = 'WAIT_FREE_TYPE';
        appendRaw('FREE scan: specifica tipo [DI/DO/AI/AO/RI] oppure lascia vuoto e premi solo Invio per tutti.', 'system');

      } else if (cmd === '8') {
        appendRaw('Reset menu.', 'system');
        resetFlow();

      } else if (cmd.toLowerCase() === 'status') {
        await refreshStatus();

      } else if (cmd.toLowerCase().startsWith('config ')) {
        const path = cmd.slice('config '.length).trim();
        appendRaw('Carico config da: ' + path, 'system');
        await callApi('POST', '/api/config/load', { path });
        await refreshStatus();

      } else if (cmd.toLowerCase() === 'config') {
        appendRaw('Carico config predefinito (./config.yaml o PGS_CONFIG_PATH)...', 'system');
        await callApi('POST', '/api/config/load', {});
        await refreshStatus();

      } else {
        appendRaw('Scelta non valida. Usa 1..8 oppure comandi: status, config, config <percorso>.', 'error');
      }
      break;
    }

    // --- IO search (menu 1..4) ---
    case 'WAIT_IO_TYPE': {
      const t = cmd.toUpperCase();
      if (!['DI','DO','AI','AO','RI'].includes(t)) {
        appendRaw('Tipo IO non valido. Valori ammessi: DI, DO, AI, AO, RI.', 'error');
        appendRaw('Tipo IO? [DI/DO/AI/AO/RI]', 'system');
      } else {
        ctx.ioType = t;
        state = 'WAIT_IO_INDEX';
        appendRaw('Indice IO (numero intero):', 'system');
      }
      break;
    }

    case 'WAIT_IO_INDEX': {
      const idx = parseInt(cmd, 10);
      if (Number.isNaN(idx)) {
        appendRaw('Indice non numerico, riprova.', 'error');
        appendRaw('Indice IO (numero intero):', 'system');
      } else {
        appendRaw(`Cerco IO ${ctx.ioType} index ${idx}...`, 'system');
        await callApi('GET',
          '/api/io/search?type=' + encodeURIComponent(ctx.ioType) +
          '&index=' + encodeURIComponent(idx)
        );
        resetFlow();
      }
      break;
    }

    // --- SYSTEM (AXIS / ALARM) ---
    case 'WAIT_SYSTEM_KIND': {
      const kind = cmd.toUpperCase();
      if (!['AXIS','ALARM'].includes(kind)) {
        appendRaw('kind non valido. Ammessi: AXIS o ALARM.', 'error');
        appendRaw('SYSTEM kind? [AXIS/ALARM]', 'system');
      } else {
        ctx.kind = kind;
        state = 'WAIT_SYSTEM_FIELD';
        appendRaw('Campo SYSTEM (es. UP, DOWN, MASTER, MASK...):', 'system');
      }
      break;
    }

    case 'WAIT_SYSTEM_FIELD': {
      if (!cmd) {
        appendRaw('Campo SYSTEM vuoto, riprova.', 'error');
        appendRaw('Campo SYSTEM (es. UP, DOWN, MASTER, MASK...):', 'system');
      } else {
        ctx.field = cmd.toUpperCase();
        state = 'WAIT_SYSTEM_INDEX';
        appendRaw('Indice SYSTEM (numero intero, es. 1):', 'system');
      }
      break;
    }

    case 'WAIT_SYSTEM_INDEX': {
      const idx = parseInt(cmd, 10);
      if (Number.isNaN(idx)) {
        appendRaw('Indice non numerico, riprova.', 'error');
        appendRaw('Indice SYSTEM (numero intero, es. 1):', 'system');
      } else {
        appendRaw(`Cerco SYSTEM kind=${ctx.kind} field=${ctx.field} index=${idx}...`, 'system');
        const params = new URLSearchParams({
          kind: ctx.kind,
          field: ctx.field,
          index: String(idx),
        });
        await callApi('GET', '/api/system/search?' + params.toString());
        resetFlow();
      }
      break;
    }

    // --- FREE scan ---
    case 'WAIT_FREE_TYPE': {
      const t = cmd.toUpperCase();
      if (!cmd) {
        appendRaw('FREE scan: tutti i tipi...', 'system');
        await callApi('GET', '/api/free/scan');
        resetFlow();
      } else if (!['DI','DO','AI','AO','RI'].includes(t)) {
        appendRaw('Tipo IO non valido per FREE. Valori ammessi: DI, DO, AI, AO, RI oppure vuoto per tutti.', 'error');
        appendRaw('FREE scan: specifica tipo [DI/DO/AI/AO/RI] oppure lascia vuoto e premi solo Invio per tutti.', 'system');
      } else {
        appendRaw('FREE scan tipo ' + t + '...', 'system');
        await callApi('GET', '/api/free/scan?type=' + encodeURIComponent(t));
        resetFlow();
      }
      break;
    }

    default: {
      appendRaw('Stato interno sconosciuto, resetto il menu.', 'error');
      resetFlow();
    }
  }
}

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const value = input.value;
    input.value = '';
    await handleEnter(value);
  });

  appendRaw('PGS-X-F Web CLI pronta.', 'system');
  printConfigQuestion();
  refreshStatus();
  input.focus();
</script>
</body>
</html>
"""

# -----------------
# Stato globale minimale per il server
# -------------------------

_CONFIG_LOADED: bool = False
_CONFIG_PATH: Optional[Path] = None


def _load_yaml_config(path: Optional[str] = None) -> Dict[str, str]:
    """
    Carica (o ricarica) il config.yaml dentro data_config.

    - se path è None, usa:
        1) variabile env PGS_CONFIG_PATH
        2) altrimenti ./config.yaml nella cwd
    """
    global _CONFIG_LOADED, _CONFIG_PATH

    if path:
        cfg_path = Path(path)
    else:
        env_path = os.environ.get("PGS_CONFIG_PATH")
        if env_path:
            cfg_path = Path(env_path)
        else:
            cfg_path = Path.cwd() / "config.yaml"

    if not cfg_path.exists():
        raise FileNotFoundError(f"config.yaml non trovato in {cfg_path}")

    populate_from_yaml_file(cfg_path)
    _CONFIG_LOADED = True
    _CONFIG_PATH = cfg_path

    # SN di commessa se disponibile
    try:
        sn_value = data_config.Config_Header[HEADER_SN]
    except Exception:
        sn_value = None

    return {
        "config_path": str(cfg_path),
        "sn": sn_value,
    }


def _ensure_config_loaded() -> None:
    """Lancia eccezione se il config non è ancora stato caricato."""
    if not _CONFIG_LOADED:
        raise RuntimeError("Config YAML non caricato. Chiama prima /api/config/load.")


# -----------------
# Helpers per FREE scan / CHECK
# -------------------------
def _parse_io_type(io_type_raw: str) -> int:
    io_type_raw = io_type_raw.upper().strip()
    if io_type_raw == "DI":
        return IO_DI
    if io_type_raw == "DO":
        return IO_DO
    if io_type_raw == "AI":
        return IO_AI
    if io_type_raw == "AO":
        return IO_AO
    if io_type_raw == "RI":
        return IO_RI
    raise ValueError(f"Tipo IO non valido: {io_type_raw}")


def _free_scan_collect(io_type_filter: Optional[int] = None) -> Dict[str, List[Dict[str, object]]]:
    """
    Replica la logica di una "FREE scan" su tutti i tipi, ma ritorna un JSON:
    {
        "DI": [...],
        "DO": [...],
        ...
    }
    """
    all_types = [IO_DI, IO_DO, IO_AI, IO_AO, IO_RI]
    result: Dict[str, List[Dict[str, object]]] = {}

    for t in all_types:
        if io_type_filter is not None and t != io_type_filter:
            continue

        entries = run_io_search(iotype=t, Ind=-1, verbose=False) or []
        key = {
            IO_DI: "DI",
            IO_DO: "DO",
            IO_AI: "AI",
            IO_AO: "AO",
            IO_RI: "RI",
        }[t]
        result[key] = entries

    return result


def _run_custom_checks_capture() -> List[str]:
    """
    Esegue custom_function() ma invece di scrivere su stdout
    accumula le righe in una lista da restituire.
    """
    lines: List[str] = []

    def _log_line(msg: str) -> None:
        lines.append(str(msg))

    # custom_function accetta un logger? Nel dubbio usiamo wrapper
    # custom_function(logger=_log_line)
    custom_function()
    return lines


# -----------------
# Flask app
# -------------------------


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        # Pagina che emula la console
        return INDEX_HTML

    exe_cfg = load_exe_config()
    debug = bool(exe_cfg.get("debug", False))

    # Tentativo best-effort di caricare il config all'avvio
    try:
        _load_yaml_config()
        logging.info("config.yaml caricato all'avvio del server Flask.")
    except Exception as e:
        logging.warning("Impossibile caricare il config all'avvio: %s", e)

    @app.get("/api/status")
    def api_status():
        """
        Ritorna lo stato base del server:
        - versione
        - se il config è caricato
        - path del config
        - SN (se disponibile)
        - se esiste un last_url per il refresh
        """
        version_info = get_version_info()

        try:
            sn_value = data_config.Config_Header[HEADER_SN]
        except Exception:
            sn_value = None

        has_last_url = bool(getattr(yaml_download, "last_url", ""))

        return jsonify(
            {
                "ok": True,
                "version": version_info,
                "config_loaded": _CONFIG_LOADED,
                "config_path": str(_CONFIG_PATH) if _CONFIG_PATH else None,
                "sn": sn_value,
                "has_last_url": has_last_url,
            }
        )

    @app.post("/api/config/load")
    def api_config_load():
        """
        (Re)carica il config.yaml.
        Body JSON opzionale: {"path": "/percorso/config.yaml"}
        """
        payload = request.get_json(silent=True) or {}
        path = payload.get("path")
        try:
            info = _load_yaml_config(path)
            return jsonify({"ok": True, **info})
        except FileNotFoundError as e:
            return jsonify({"ok": False, "error": str(e)}), 404
        except Exception as e:
            logging.exception("Errore durante il caricamento del config.yaml")
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.post("/api/config/prepare")
    def api_config_prepare():
        """
        Prepara il config come la CLI (choose_and_prepare_config):
        - mode="local"   -> usa _load_yaml_config() sul file locale
        - mode="remote"  -> scarica config.yaml da IP/URL usando _build_download_url + _download_to_config
        - mode="refresh" -> rifà il download da last_url (fetch_again)
        - mode="save"    -> salva "config {sn} {ver} {date}.yaml" come nel CLI
        """
        payload = request.get_json(silent=True) or {}
        mode = payload.get("mode", "local")
        ip = payload.get("ip")
        url = payload.get("url")
        version = payload.get("version") or payload.get("ver")

        try:
            if mode == "local":
                # semplice reload locale
                info = _load_yaml_config()
                return jsonify({"ok": True, "mode": "local", **info})

            elif mode == "remote":
                if not (ip or url):
                    return jsonify(
                        {"ok": False, "error": "Serve 'ip' o 'url' per mode=remote."}
                    ), 400

                if not url:
                    # stesse regole del CLI: IP -> URL completo
                    url = _build_download_url(ip)

                # usa la stessa funzione del CLI: scarica su config.yaml e aggiorna last_url
                cfg_path = _download_to_config(url)
                info = _load_yaml_config(str(cfg_path))
                return jsonify({"ok": True, "mode": "remote", "source": url, **info})

            elif mode == "refresh":
                # equivalente a fetch_again() del CLI
                cfg_path = fetch_again()
                if cfg_path is None:
                    return jsonify(
                        {
                            "ok": False,
                            "error": "Nessun URL precedente: usa prima mode=remote.",
                        }
                    ), 400

                info = _load_yaml_config(str(cfg_path))
                return jsonify(
                    {
                        "ok": True,
                        "mode": "refresh",
                        "source": getattr(yaml_download, "last_url", None),
                        **info,
                    }
                )

            elif mode == "save":
                if not version:
                    return jsonify(
                        {
                            "ok": False,
                            "error": "Campo 'version' mancante per mode=save.",
                        }
                    ), 400

                try:
                    sn_value = data_config.Config_Header[HEADER_SN]
                except Exception:
                    return jsonify(
                        {
                            "ok": False,
                            "error": "SN non disponibile: carica prima un config valido.",
                        }
                    ), 400

                today = datetime.datetime.now().strftime("%Y%m%d")
                ok = save_version(sn=sn_value, ver=version, date=today)
                return jsonify(
                    {
                        "ok": ok,
                        "mode": "save",
                        "sn": sn_value,
                        "version": version,
                        "date": today,
                    }
                )

            else:
                return jsonify({"ok": False, "error": f"mode non valido: {mode}"}), 400

        except FileNotFoundError as e:
            return jsonify({"ok": False, "error": str(e)}), 404
        except Exception as e:
            logging.exception("Errore in api_config_prepare")
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.get("/api/io/search")
    def api_io_search():
        """
        Replica 1..4 del menu CLI:
        GET /api/io/search?type=DI&index=123
        """
        try:
            _ensure_config_loaded()
        except RuntimeError as e:
            return jsonify({"ok": False, "error": str(e)}), 503

        io_type_raw = request.args.get("type", "DI")
        idx = request.args.get("index", type=int)
        if idx is None:
            return jsonify({"ok": False, "error": "Parametro 'index' mancante o non numerico."}), 400

        try:
            iotype = _parse_io_type(io_type_raw)
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400

        results = run_io_search(iotype=iotype, Ind=idx, verbose=False) or []
        return jsonify(
            {
                "ok": True,
                "type": io_type_raw.upper(),
                "index": idx,
                "results": results,
            }
        )

    @app.get("/api/system/search")
    def api_system_search():
        """
        Replica voce 5 (SYSTEM) del menu CLI, ma senza tutti i prompt:
        GET /api/system/search?kind=AXIS&field=UP&index=1
        GET /api/system/search?kind=ALARM&field=MASK&index=3
        """
        try:
            _ensure_config_loaded()
        except RuntimeError as e:
            return jsonify({"ok": False, "error": str(e)}), 503

        kind = request.args.get("kind", "AXIS").upper()
        field = request.args.get("field", "").upper()
        index = request.args.get("index", type=int)
        if not field or index is None:
            return jsonify({"ok": False, "error": "Parametri 'field' e 'index' sono obbligatori."}), 400

        try:
            if kind == "AXIS":
                number = make_axis_sys_addr(field, index)
            elif kind == "ALARM":
                number = make_alarm_sys_addr(field, index)
            else:
                return jsonify({"ok": False, "error": "kind deve essere AXIS o ALARM."}), 400
        except Exception as e:
            return jsonify({"ok": False, "error": f"Errore nel calcolo indirizzo SYSTEM: {e}"}), 400

        human = decode_sys_addr(number) or f"{kind}.{field}[{index}]"
        refs = run_io_search(iotype=IO_DI, Ind=number, verbose=False) or []

        return jsonify(
            {
                "ok": True,
                "kind": kind,
                "field": field,
                "index": index,
                "number": number,
                "human": human,
                "refs": refs,
            }
        )

    @app.get("/api/free/scan")
    def api_free_scan():
        """
        Replica voce 7 (FREE) del menu CLI:
        GET /api/free/scan          -> tutti i tipi
        GET /api/free/scan?type=DI  -> solo DI
        """
        try:
            _ensure_config_loaded()
        except RuntimeError as e:
            return jsonify({"ok": False, "error": str(e)}), 503

        io_type_raw = request.args.get("type")
        if io_type_raw:
            try:
                io_type_filter = _parse_io_type(io_type_raw)
            except ValueError as e:
                return jsonify({"ok": False, "error": str(e)}), 400
        else:
            io_type_filter = None

        all_data = _free_scan_collect(io_type_filter)
        return jsonify({"ok": True, "types": list(all_data.keys()), "data": all_data})

    @app.get("/api/check")
    def api_check():
        """
        Replica voce 6 (CHECK) del menu CLI:
        esegue custom_function() e ritorna le righe loggate.
        """
        try:
            _ensure_config_loaded()
        except RuntimeError as e:
            return jsonify({"ok": False, "error": str(e)}), 503

        lines = _run_custom_checks_capture()
        return jsonify({"ok": True, "lines": lines})

    # Debug Flask
    app.debug = debug
    return app


# Istanza globale per "flask run"
app = create_app()


if __name__ == "__main__":
    # Avvio diretto: python -m utils.web.server
    cfg = load_exe_config()
    debug = bool(cfg.get("debug", False))
    app.run(host="0.0.0.0", port=5000, debug=debug)
