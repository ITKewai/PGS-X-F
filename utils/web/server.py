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
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional

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
      display: flex;
      min-height: 100vh;
      align-items: stretch;
      justify-content: center;
    }
    #app {
      width: 100%;
      height: 100vh;        /* prende TUTTA l’altezza */
      margin: 0;            /* niente margini */
      border-radius: 0;     /* niente bordi arrotondati, stile terminale pieno */
      border: none;         /* volendo puoi tenere il bordo se ti piace */
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

  let state = 'WAIT_MAIN_CHOICE';
  let ctx = {};

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
      if (data && data.sn) {
        statusLeft.textContent = 'PGS-X-F Web CLI · SN: ' + data.sn;
      }
    } catch(e) {
      // già loggato in console
    }
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
    if (!cmd) return;

    appendLine(cmd, 'cmd'); // echo comando

    switch (state) {
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
          appendRaw('Scelta non valida. Usa 1,5,6,7,8 oppure comandi: status, config, config <percorso>', 'error');
        }
        break;
      }

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
          await callApi('GET', '/api/io/search?type=' + encodeURIComponent(ctx.ioType) + '&index=' + encodeURIComponent(idx));
          resetFlow();
        }
        break;
      }

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
          appendRaw('Campo vuoto, riprova.', 'error');
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

      case 'WAIT_FREE_TYPE': {
        const t = cmd.toUpperCase();
        if (!cmd) {
          appendRaw('FREE scan di tutti i tipi...', 'system');
          await callApi('GET', '/api/free/scan');
          resetFlow();
        } else if (!['DI','DO','AI','AO','RI'].includes(t)) {
          appendRaw('Tipo IO non valido. Valori ammessi: DI, DO, AI, AO, RI, oppure premi solo Invio per tutti.', 'error');
          appendRaw('FREE scan: specifica tipo [DI/DO/AI/AO/RI] oppure premi solo Invio per tutti.', 'system');
        } else {
          appendRaw('FREE scan tipo ' + t + '...', 'system');
          await callApi('GET', '/api/free/scan?type=' + encodeURIComponent(t));
          resetFlow();
        }
        break;
      }

      default: {
        // fallback: reset
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

  // bootstrap
  appendRaw('PGS-X-F Web CLI pronta.', 'system');
  appendRaw('Comandi extra: status | config | config <percorso>', 'system');
  printMenu();
  refreshStatus();
  input.focus();
</script>
</body>
</html>
"""


# -----------------------------------------------------------------------------
# Stato globale minimale per il server
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# Helpers di dominio (wrappers "web friendly")
# -----------------------------------------------------------------------------
_IO_TYPE_MAP: Dict[str, int] = {
    "DI": IO_DI,
    "AI": IO_AI,
    "DO": IO_DO,
    "AO": IO_AO,
    "RI": IO_RI,
}


def _parse_io_type(raw: str) -> int:
    key = (raw or "").strip().upper()
    if key not in _IO_TYPE_MAP:
        raise ValueError(f"Tipo IO non valido: {raw!r}. Valori ammessi: DI, AI, DO, AO, RI.")
    return _IO_TYPE_MAP[key]


def _free_scan_collect(iotype: int) -> Dict[int, List[str]]:
    """
    Versione "web" di run_free_scan:
    restituisce un dict {indice: [riferimenti...]} invece di stampare sul log.
    """
    from utils.exports.tia_constants import MAX_DI, MAX_AI, MAX_DO, MAX_AO  # type: ignore[attr-defined]

    if iotype == IO_DI:
        io_list = data_config.IO_DI_List
        label = "DI"
        max_len = MAX_DI + 1
    elif iotype == IO_DO:
        io_list = data_config.IO_DO_List
        label = "DO"
        max_len = MAX_DO + 1
    elif iotype == IO_AI:
        io_list = data_config.IO_AI_List
        label = "AI"
        max_len = MAX_AI + 1
    elif iotype == IO_AO:
        io_list = data_config.IO_AO_List
        label = "AO"
        max_len = MAX_AO + 1
    elif iotype == IO_RI:
        io_list = data_config.IO_RI_List
        label = "RI"
        max_len = len(data_config.IO_RI_List)
    else:
        raise ValueError(f"Tipo IO sconosciuto: {iotype}")

    if not io_list:
        return {}

    out: Dict[int, List[str]] = {}
    for i, param in enumerate(io_list[:max_len]):
        name = getattr(param, "name", "")
        if name == "" or str(name).strip().upper() == "FREE":
            refs = run_io_search(iotype=iotype, Ind=i, verbose=False) or []
            if refs:
                out[i] = refs

    return out


def _run_custom_checks_capture() -> List[str]:
    """
    Esegue custom_function() catturando ciò che viene scritto sul logger
    e lo restituisce come lista di righe.
    """
    buf = StringIO()
    handler = logging.StreamHandler(buf)
    handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    try:
        custom_function()
    finally:
        root_logger.removeHandler(handler)

    buf.seek(0)
    lines = [line.rstrip("\n") for line in buf.getvalue().splitlines()]
    return [ln for ln in lines if ln.strip()]


# -----------------------------------------------------------------------------
# Flask app
# -----------------------------------------------------------------------------
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
        logging.warning(f"Impossibile caricare config.yaml all'avvio: {e}")

    @app.get("/api/status")
    def api_status():
        """
        Ritorna info base su versione e stato del config.
        """
        sn_value = None
        if _CONFIG_LOADED:
            try:
                sn_value = data_config.Config_Header[HEADER_SN]
            except Exception:
                sn_value = None

        return jsonify(
            {
                "version": get_version_info(),
                "config_loaded": _CONFIG_LOADED,
                "config_path": str(_CONFIG_PATH) if _CONFIG_PATH else None,
                "sn": sn_value,
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

        kind = (request.args.get("kind") or "AXIS").strip().upper()
        field = (request.args.get("field") or "").strip().upper()
        index = request.args.get("index", type=int)

        if not field:
            return jsonify({"ok": False, "error": "Parametro 'field' mancante."}), 400
        if index is None:
            return jsonify({"ok": False, "error": "Parametro 'index' mancante o non numerico."}), 400

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
                "system_number": number,
                "decoded": human,
                "results": refs,
            }
        )

    @app.get("/api/free/scan")
    def api_free_scan():
        """
        Replica voce 7 (FREE) del menu CLI:
        - senza parametri: scansiona DI, DO, AI, AO, RI
        - con ?type=DI: solo quel tipo
        """
        try:
            _ensure_config_loaded()
        except RuntimeError as e:
            return jsonify({"ok": False, "error": str(e)}), 503

        io_type_raw = request.args.get("type")
        if io_type_raw:
            try:
                iotype = _parse_io_type(io_type_raw)
            except ValueError as e:
                return jsonify({"ok": False, "error": str(e)}), 400

            data = _free_scan_collect(iotype)
            return jsonify(
                {
                    "ok": True,
                    "types": [io_type_raw.upper()],
                    "data": {str(k): v for k, v in data.items()},
                }
            )

        # Nessun type -> tutti
        all_data = {}
        for key in ["DI", "DO", "AI", "AO", "RI"]:
            try:
                iotype = _parse_io_type(key)
                all_data[key] = {str(k): v for k, v in _free_scan_collect(iotype).items()}
            except Exception as e:
                all_data[key] = {"error": str(e)}

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
