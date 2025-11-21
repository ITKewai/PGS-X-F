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
  <title>PGS-X-F – Web console</title>
  <style>
    :root {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color-scheme: dark;
    }
    body {
      margin: 0;
      background: #050810;
      color: #e5e7eb;
      display: flex;
      min-height: 100vh;
      align-items: stretch;
      justify-content: center;
    }
    #app {
      width: 100%;
      max-width: 1100px;
      margin: 1.5rem;
      border-radius: 18px;
      border: 1px solid #1f2937;
      background: radial-gradient(circle at top left, #111827 0, #020617 45%);
      box-shadow: 0 18px 45px rgba(0,0,0,0.6);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    header {
      padding: 0.75rem 1.5rem;
      border-bottom: 1px solid #111827;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: linear-gradient(to right, rgba(15,23,42,0.9), rgba(15,23,42,0.3));
    }
    header h1 {
      font-size: 0.95rem;
      font-weight: 600;
      letter-spacing: .08em;
      text-transform: uppercase;
      margin: 0;
      color: #9ca3af;
    }
    header .pill {
      font-size: 0.75rem;
      padding: 0.15rem 0.6rem;
      border-radius: 999px;
      border: 1px solid #374151;
      background: rgba(17,24,39,0.8);
      color: #9ca3af;
    }
    main {
      display: grid;
      grid-template-columns: minmax(0, 3fr) minmax(260px, 2fr);
      gap: 0;
      min-height: 480px;
    }
    @media (max-width: 900px) {
      main {
        grid-template-columns: 1fr;
      }
    }
    .console {
      padding: 1rem 1.25rem;
      background: radial-gradient(circle at top left, #020617 0, #000 55%);
      border-right: 1px solid #111827;
      font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.78rem;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .console-line {
      line-height: 1.45;
    }
    .console-line.system { color: #6b7280; }
    .console-line.ok { color: #22c55e; }
    .console-line.error { color: #f97373; }
    .console-line.cmd { color: #e5e7eb; }
    .console .prompt {
      color: #4ade80;
    }
    .controls {
      padding: 1rem 1.25rem 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    .section-title {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: #9ca3af;
      margin-bottom: 0.35rem;
    }
    .card {
      border-radius: 14px;
      border: 1px solid #111827;
      background: rgba(15,23,42,0.85);
      padding: 0.75rem 0.9rem;
    }
    .row {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      margin-bottom: 0.35rem;
      flex-wrap: wrap;
    }
    label {
      font-size: 0.75rem;
      color: #9ca3af;
    }
    input, select {
      background: #020617;
      border-radius: 999px;
      border: 1px solid #1f2937;
      padding: 0.35rem 0.7rem;
      font-size: 0.78rem;
      color: #e5e7eb;
      outline: none;
      min-width: 0;
      flex: 1;
    }
    input:focus, select:focus {
      border-color: #22c55e;
      box-shadow: 0 0 0 1px rgba(34,197,94,0.35);
    }
    button {
      border-radius: 999px;
      border: 1px solid #16a34a;
      background: radial-gradient(circle at top left, #22c55e, #15803d);
      color: #022c22;
      font-size: 0.78rem;
      font-weight: 600;
      padding: 0.4rem 0.9rem;
      cursor: pointer;
      white-space: nowrap;
    }
    button.secondary {
      border-color: #4b5563;
      background: #020617;
      color: #e5e7eb;
      font-weight: 500;
    }
    button:active {
      transform: translateY(1px);
    }
    small.hint {
      font-size: 0.7rem;
      color: #6b7280;
      display: block;
      margin-top: 0.25rem;
    }
    footer {
      border-top: 1px solid #111827;
      padding: 0.35rem 1.25rem 0.5rem;
      font-size: 0.7rem;
      color: #4b5563;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  </style>
</head>
<body>
<div id="app">
  <header>
    <h1>PGS-X-F · Web console</h1>
    <div class="pill" id="status-pill">config: sconosciuto</div>
  </header>
  <main>
    <div class="console" id="console"></div>
    <div class="controls">
      <div class="card">
        <div class="section-title">Config</div>
        <div class="row">
          <label for="config-path">Percorso config.yaml (opzionale)</label>
        </div>
        <div class="row">
          <input id="config-path" placeholder="es. C:/progetti/PGS/config.yaml o lascia vuoto per ./config.yaml" />
        </div>
        <div class="row">
          <button id="btn-load-config">Carica config</button>
          <button class="secondary" id="btn-status">Status</button>
        </div>
        <small class="hint">Uguale alla scelta del config nel main CLI. Se non specifichi nulla usa il config.yaml nella cartella di esecuzione.</small>
      </div>

      <div class="card">
        <div class="section-title">Ricerca IO (menu 1..4)</div>
        <div class="row">
          <label for="io-type">Tipo</label>
          <select id="io-type">
            <option value="DI">DI</option>
            <option value="AI">AI</option>
            <option value="DO">DO</option>
            <option value="AO">AO</option>
            <option value="RI">RI</option>
          </select>
          <label for="io-index">Indice</label>
          <input id="io-index" type="number" min="0" step="1" placeholder="es. 123" />
        </div>
        <div class="row">
          <button id="btn-io-search">Cerca</button>
        </div>
        <small class="hint">Chiama /api/io/search?type=DI&index=123 come nel main quando scegli 1..4.</small>
      </div>

      <div class="card">
        <div class="section-title">System (menu 5)</div>
        <div class="row">
          <label for="system-kind">Kind</label>
          <select id="system-kind">
            <option value="AXIS">AXIS</option>
            <option value="ALARM">ALARM</option>
          </select>
        </div>
        <div class="row">
          <label for="system-field">Campo</label>
          <input id="system-field" placeholder="es. UP, DOWN, MASTER, MASK..." />
        </div>
        <div class="row">
          <label for="system-index">Indice</label>
          <input id="system-index" type="number" min="0" step="1" placeholder="es. 1" />
        </div>
        <div class="row">
          <button id="btn-system-search">Cerca SYSTEM</button>
        </div>
        <small class="hint">Wrapper di /api/system/search. Usa gli stessi parametri che useresti nel CLI.</small>
      </div>

      <div class="card">
        <div class="section-title">FREE & CHECK (menu 7 e 6)</div>
        <div class="row">
          <label for="free-type">FREE type (opzionale)</label>
          <select id="free-type">
            <option value="">Tutti</option>
            <option value="DI">DI</option>
            <option value="AI">AI</option>
            <option value="DO">DO</option>
            <option value="AO">AO</option>
            <option value="RI">RI</option>
          </select>
        </div>
        <div class="row">
          <button id="btn-free-scan">FREE scan</button>
          <button class="secondary" id="btn-check">CHECK custom_function()</button>
        </div>
        <small class="hint">Replica la voce 7 (FREE) e 6 (CHECK) del menu CLI.</small>
      </div>
    </div>
  </main>
  <footer>
    <span id="footer-version">Versione: sconosciuta</span>
    <span>Web layer · same core di main.py</span>
  </footer>
</div>

<script>
  const consoleEl = document.getElementById('console');
  const statusPill = document.getElementById('status-pill');
  const footerVersion = document.getElementById('footer-version');

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
    try {
      return JSON.stringify(obj, null, 2);
    } catch (e) {
      return String(obj);
    }
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
    const data = await callApi('GET', '/api/status');
    if (data && data.version) {
      footerVersion.textContent = 'Versione: ' + data.version;
    }
    if (data && data.config_loaded) {
      statusPill.textContent = 'config: caricato (' + (data.config_path || 'n/d') + ')';
      statusPill.style.borderColor = '#22c55e';
      statusPill.style.color = '#bbf7d0';
    } else {
      statusPill.textContent = 'config: non caricato';
      statusPill.style.borderColor = '#f97373';
      statusPill.style.color = '#fecaca';
    }
  }

  document.getElementById('btn-status').addEventListener('click', () => {
    refreshStatus();
  });

  document.getElementById('btn-load-config').addEventListener('click', async () => {
    const path = document.getElementById('config-path').value.trim();
    const body = path ? { path } : {};
    await callApi('POST', '/api/config/load', body);
    await refreshStatus();
  });

  document.getElementById('btn-io-search').addEventListener('click', async () => {
    const type = document.getElementById('io-type').value;
    const idx = document.getElementById('io-index').value;
    if (idx === '') {
      appendRaw('Indice IO mancante', 'error');
      return;
    }
    const url = '/api/io/search?type=' + encodeURIComponent(type) + '&index=' + encodeURIComponent(idx);
    await callApi('GET', url);
  });

  document.getElementById('btn-system-search').addEventListener('click', async () => {
    const kind = document.getElementById('system-kind').value;
    const field = document.getElementById('system-field').value.trim();
    const idx = document.getElementById('system-index').value;
    if (!field || idx === '') {
      appendRaw('Campo e indice SYSTEM sono obbligatori', 'error');
      return;
    }
    const params = new URLSearchParams({
      kind,
      field,
      index: idx
    });
    const url = '/api/system/search?' + params.toString();
    await callApi('GET', url);
  });

  document.getElementById('btn-free-scan').addEventListener('click', async () => {
    const type = document.getElementById('free-type').value;
    let url = '/api/free/scan';
    if (type) {
      url += '?type=' + encodeURIComponent(type);
    }
    await callApi('GET', url);
  });

  document.getElementById('btn-check').addEventListener('click', async () => {
    await callApi('GET', '/api/check');
  });

  appendRaw('PGS-X-F web console pronta. Usa i pannelli a destra come useresti il menu di main.py.', 'system');
  refreshStatus();
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
