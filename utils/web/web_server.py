#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_server.py
-----------
Server Flask che espone l'interfaccia web per il programma di ricerca configurazioni.
Ascolta su http://127.0.0.1:6666

API Endpoints:
  GET  /                          - Pagina HTML principale
  GET  /api/status                - Status del programma
  GET  /api/io-types              - Tipi di IO disponibili
  POST /api/search                - Ricerca un IO
  GET  /api/axis-list             - Lista assi disponibili
  GET  /api/alarm-list            - Lista allarmi disponibili
  POST /api/search-system         - Ricerca di sistema (AXIS/ALARM)
  POST /api/load-config           - Carica un nuovo config
"""

from flask import Flask, render_string, request, jsonify
import json
import logging
from pathlib import Path

from core_logic import SearchState

# Configurazione Flask
app = Flask(__name__, static_folder=None, template_folder=None)
app.config['JSON_SORT_KEYS'] = False

# Stato globale della ricerca
search_state = SearchState()

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== HTML Template ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>PSG-X FindIndex - Web Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            height: 100vh;
            overflow: hidden;
        }

        .container {
            display: flex;
            height: 100vh;
        }

        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
            overflow-y: auto;
            background: linear-gradient(135deg, #1a1a1a 0%, #252525 100%);
        }

        .header {
            margin-bottom: 30px;
            border-bottom: 2px solid #ff9800;
            padding-bottom: 15px;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 600;
            color: #ff9800;
        }

        .header p {
            font-size: 14px;
            color: #888;
            margin-top: 5px;
        }

        .section {
            margin-bottom: 25px;
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ff9800;
        }

        .section-title {
            font-size: 16px;
            font-weight: 600;
            color: #ff9800;
            margin-bottom: 12px;
        }

        .form-group {
            margin-bottom: 12px;
            display: flex;
            gap: 10px;
            align-items: center;
        }

        label {
            font-size: 14px;
            color: #bbb;
            min-width: 120px;
        }

        select, input[type="text"], input[type="number"] {
            flex: 1;
            padding: 12px;
            background: #333;
            color: #e0e0e0;
            border: 1px solid #444;
            border-radius: 4px;
            font-size: 14px;
        }

        select:focus, input[type="text"]:focus, input[type="number"]:focus {
            outline: none;
            border-color: #ff9800;
            background: #3a3a3a;
        }

        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        button {
            flex: 1;
            padding: 14px 20px;
            background: #ff9800;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover {
            background: #f08000;
        }

        button:active {
            background: #e68900;
        }

        .results {
            background: #222;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 15px;
            margin-top: 15px;
            max-height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #4caf50;
        }

        .results.empty {
            color: #888;
        }

        .results > div {
            margin-bottom: 8px;
            white-space: pre-wrap;
            word-break: break-word;
        }

        /* ==================== NUMERIC KEYPAD ==================== */
        .keypad-container {
            width: 280px;
            background: #2a2a2a;
            border: 2px solid #ff9800;
            border-radius: 8px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .keypad-title {
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            color: #ff9800;
            margin-bottom: 5px;
        }

        .keypad-display {
            background: #1a1a1a;
            border: 1px solid #444;
            padding: 10px;
            text-align: right;
            font-size: 20px;
            font-weight: 600;
            color: #4caf50;
            font-family: 'Courier New', monospace;
            border-radius: 4px;
            min-height: 40px;
            word-break: break-all;
        }

        .keypad-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 8px;
        }

        .key {
            padding: 16px;
            background: #404040;
            color: #e0e0e0;
            border: 1px solid #555;
            border-radius: 4px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.1s;
            user-select: none;
            touch-action: manipulation;
        }

        .key:active {
            background: #555;
            transform: scale(0.95);
        }

        .key.special {
            background: #d32f2f;
            color: white;
        }

        .key.special:active {
            background: #b71c1c;
        }

        .key.enter {
            background: #4caf50;
            color: white;
            grid-column: 2 / 4;
        }

        .key.enter:active {
            background: #388e3c;
        }

        /* ==================== RIGHT PANEL ==================== */
        .right-panel {
            width: 320px;
            background: #2a2a2a;
            border-left: 2px solid #ff9800;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            overflow-y: auto;
        }

        @media (max-width: 1024px) {
            .container {
                flex-direction: column;
            }

            .main-content {
                flex: 1;
            }

            .right-panel {
                width: 100%;
                border-left: none;
                border-top: 2px solid #ff9800;
                max-height: 200px;
                padding: 15px;
            }

            .keypad-container {
                margin-top: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="header">
                <h1>PGS-X FindIndex</h1>
                <p>Interfaccia Web per Ricerca Configurazioni</p>
            </div>

            <!-- SEZIONE: Ricerca IO -->
            <div class="section">
                <div class="section-title">Ricerca I/O</div>
                <div class="form-group">
                    <label>Tipo I/O:</label>
                    <select id="ioType">
                        <option value="1">DI - Digital Input</option>
                        <option value="2">AI - Analog Input</option>
                        <option value="3">DO - Digital Output</option>
                        <option value="4">AO - Analog Output</option>
                        <option value="5">SYSTEM</option>
                        <option value="7">FREE - Scan automatico</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Numero:</label>
                    <input type="number" id="ioNumber" placeholder="Inserisci numero" min="0">
                </div>
                <div class="button-group">
                    <button onclick="searchIO()">Cerca</button>
                </div>
                <div id="ioResults" class="results empty">Nessun risultato</div>
            </div>

            <!-- SEZIONE: Ricerca SYSTEM -->
            <div class="section">
                <div class="section-title">Ricerca SYSTEM</div>
                <div class="form-group">
                    <label>Tipo Sistema:</label>
                    <select id="sysType">
                        <option value="AXIS">AXIS</option>
                        <option value="ALARM">ALARM</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>INDEX:</label>
                    <input type="number" id="sysIndex" placeholder="0 - 99" min="0">
                </div>
                <div class="form-group">
                    <label>FIELD:</label>
                    <input type="text" id="sysField" placeholder="Es: COUNT, SPEED, ...">
                </div>
                <div class="button-group">
                    <button onclick="searchSystem()">Ricerca SYSTEM</button>
                </div>
                <div id="sysResults" class="results empty">Nessun risultato</div>
            </div>
        </div>

        <!-- RIGHT PANEL: KEYPAD -->
        <div class="right-panel">
            <div class="keypad-container">
                <div class="keypad-title">Tastierino Numerico</div>
                <div class="keypad-display" id="keypadDisplay"></div>
                <div class="keypad-grid">
                    <div class="key" onclick="keypadAppend('7')">7</div>
                    <div class="key" onclick="keypadAppend('8')">8</div>
                    <div class="key" onclick="keypadAppend('9')">9</div>
                    <div class="key special" onclick="keypadBackspace()">⌫</div>

                    <div class="key" onclick="keypadAppend('4')">4</div>
                    <div class="key" onclick="keypadAppend('5')">5</div>
                    <div class="key" onclick="keypadAppend('6')">6</div>
                    <div class="key enter" onclick="keypadEnter()">↵</div>

                    <div class="key" onclick="keypadAppend('1')">1</div>
                    <div class="key" onclick="keypadAppend('2')">2</div>
                    <div class="key" onclick="keypadAppend('3')">3</div>

                    <div class="key" onclick="keypadAppend('0')">0</div>
                    <div class="key" onclick="keypadAppend('-')">-</div>
                    <div class="key" onclick="keypadAppend('.')">.</div>
                    <div class="key special" onclick="keypadEscape()">ESC</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ==================== KEYPAD LOGIC ====================
        let activeInput = null;
        let keypadValue = '';

        // Traccia quale input ha il focus
        document.addEventListener('focusin', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') {
                activeInput = e.target;
                keypadValue = e.target.value || '';
                updateKeypadDisplay();
            }
        });

        function keypadAppend(char) {
            if (!activeInput) return;
            keypadValue += char;
            activeInput.value = keypadValue;
            updateKeypadDisplay();
        }

        function keypadBackspace() {
            if (!activeInput) return;
            keypadValue = keypadValue.slice(0, -1);
            activeInput.value = keypadValue;
            updateKeypadDisplay();
        }

        function keypadEnter() {
            if (!activeInput) return;
            // Simula un invio sulla tastiera
            activeInput.dispatchEvent(new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13
            }));
        }

        function keypadEscape() {
            if (!activeInput) return;
            keypadValue = '';
            activeInput.value = '';
            updateKeypadDisplay();
        }

        function updateKeypadDisplay() {
            document.getElementById('keypadDisplay').textContent = keypadValue;
        }

        // ==================== SEARCH FUNCTIONS ====================
        async function searchIO() {
            const ioType = document.getElementById('ioType').value;
            const ioNumber = document.getElementById('ioNumber').value;

            if (!ioNumber) {
                alert('Inserisci un numero');
                return;
            }

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ io_type: parseInt(ioType), io_number: parseInt(ioNumber) })
                });

                const data = await response.json();
                const resultsDiv = document.getElementById('ioResults');

                if (data.success) {
                    if (data.results.length > 0) {
                        resultsDiv.innerHTML = data.results.map(r => `<div>${escapeHtml(r)}</div>`).join('');
                        resultsDiv.classList.remove('empty');
                    } else {
                        resultsDiv.innerHTML = 'Nessun risultato trovato';
                        resultsDiv.classList.add('empty');
                    }
                } else {
                    resultsDiv.innerHTML = escapeHtml(data.message);
                    resultsDiv.classList.add('empty');
                }
            } catch (e) {
                alert('Errore: ' + e);
            }
        }

        async function searchSystem() {
            const sysType = document.getElementById('sysType').value;
            const sysIndex = document.getElementById('sysIndex').value;
            const sysField = document.getElementById('sysField').value;

            if (!sysIndex || !sysField) {
                alert('Inserisci INDEX e FIELD');
                return;
            }

            try {
                const response = await fetch('/api/search-system', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sys_type: sysType,
                        index: parseInt(sysIndex),
                        field: sysField
                    })
                });

                const data = await response.json();
                const resultsDiv = document.getElementById('sysResults');

                if (data.success) {
                    resultsDiv.innerHTML = `<div>${escapeHtml(data.message)}</div>`;
                    resultsDiv.classList.remove('empty');
                } else {
                    resultsDiv.innerHTML = escapeHtml(data.message);
                    resultsDiv.classList.add('empty');
                }
            } catch (e) {
                alert('Errore: ' + e);
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Focus sul primo input all'avvio
        window.addEventListener('load', function() {
            document.getElementById('ioNumber').focus();
        });
    </script>
</body>
</html>
"""


# ==================== ROUTE HANDLERS ====================

@app.route('/')
def index():
    """Serve la pagina HTML principale."""
    return render_string(HTML_TEMPLATE)


@app.route('/api/status', methods=['GET'])
def api_status():
    """Restituisce lo status del programma."""
    return jsonify({
        'loaded': search_state.config_loaded,
        'current_sn': search_state.current_sn,
        'config_path': str(search_state.current_config_path) if search_state.current_config_path else None
    })


@app.route('/api/io-types', methods=['GET'])
def api_io_types():
    """Restituisce i tipi di IO disponibili."""
    return jsonify(search_state.get_io_types())


@app.route('/api/search', methods=['POST'])
def api_search():
    """Ricerca un IO specifico."""
    data = request.json
    io_type = data.get('io_type', 1)
    io_number = data.get('io_number', 0)

    results = search_state.search_io(io_type, io_number)
    return jsonify({
        'success': True,
        'results': results
    })


@app.route('/api/axis-list', methods=['GET'])
def api_axis_list():
    """Restituisce la lista degli assi."""
    return jsonify(search_state.get_axis_list())


@app.route('/api/alarm-list', methods=['GET'])
def api_alarm_list():
    """Restituisce la lista degli allarmi."""
    return jsonify(search_state.get_alarm_list())


@app.route('/api/search-system', methods=['POST'])
def api_search_system():
    """Ricerca di sistema (AXIS/ALARM)."""
    data = request.json
    sys_type = data.get('sys_type', 'AXIS')
    index = data.get('index', 0)
    field = data.get('field', '')

    success, message = search_state.search_system(sys_type, index, field)
    return jsonify({
        'success': success,
        'message': message
    })


@app.route('/api/load-config', methods=['POST'])
def api_load_config():
    """Carica un nuovo file di configurazione."""
    data = request.json
    config_path = data.get('config_path')

    success, message = search_state.load_config(Path(config_path) if config_path else None)
    return jsonify({
        'success': success,
        'message': message
    })


def run_web_server(host: str = '127.0.0.1', port: int = 6666):
    """Avvia il server Flask."""
    logger.info(f"\n{'=' * 60}")
    logger.info("🌐 Web Server in avvio...")
    logger.info(f"📍 Indirizzo: http://{host}:{port}")
    logger.info(f"{'=' * 60}\n")
    app.run(host=host, port=port, debug=False, use_reloader=False)
