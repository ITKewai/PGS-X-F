#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo per caricare e sanificare il file YAML di configurazione
(estratto da main.py per maggiore chiarezza).
"""
import logging
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional


def _sanitize_yaml_like(text: str) -> str:
    """
    Converte sequenze in stile YAML con elementi vuoti/trailing comma in 'null'.
    Esempi:
      [a, b,,]   -> [a, b, null, null]
      [,a,,b,]   -> [null, a, null, b, null]
    NOTE: approccio best-effort basato su regex; pensato per casi reali del file.
    """
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r',\s*,', ', null,', text)  # elemento vuoto tra due virgole
    text = re.sub(r'\[\s*,', '[ null,', text)  # vuoto subito dopo '['
    text = re.sub(r'\[\s*,', '[ null,', text)  # vuoto subito dopo '['
    text = re.sub(r',\s*\]', ', null]', text)  # vuoto prima di ']'
    return text


def _sanitize_pstring_flow_lists(text: str) -> str:
    """
    Converte pstring: [a,b,,] -> pstring: ['a', 'b', null, null]
    (solo per le righe 'pstring', non tocca il resto)
    """

    def fix(match: re.Match) -> str:
        indent = match.group(1) or ""
        inner = match.group(2) or ""
        tokens = [t.strip() for t in inner.split(",")]
        out = []
        for t in tokens:
            if t == "" or t.lower() in {"none", "null"}:
                out.append("null")
            else:
                # se contiene spazi e non è già quotato, quota
                if not (t.startswith("'") and t.endswith("'")) and not (t.startswith('"') and t.endswith('"')):
                    if " " in t:
                        t = "'" + t.replace("'", "''") + "'"
                out.append(t)
        return f"{indent}pstring: [{', '.join(out)}]"

    # solo righe pstring in stile flow
    return re.sub(r"(?mi)^(\s*)pstring\s*:\s*\[(.*?)\]\s*$", fix, text)


def _is_row(x: Any) -> bool:
    return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)


def _group_io(io_node: Any, keys=('di', 'ai', 'do', 'ao', 'ri', 'fb')) -> Dict[str, List[list]]:
    grouped: Dict[str, List[list]] = {k: [] for k in keys}

    if isinstance(io_node, list):
        for item in io_node:
            if isinstance(item, dict) and len(item) == 1:
                k, v = next(iter(item.items()))
                kl = str(k).lower()
                if kl in grouped:
                    if _is_row(v):
                        grouped[kl].append(v)
                    elif isinstance(v, list):
                        grouped[kl].extend([el for el in v if _is_row(el)])
    elif isinstance(io_node, dict):
        for k, v in io_node.items():
            kl = str(k).lower()
            if kl in grouped:
                if _is_row(v):
                    grouped[kl].append(v)
                elif isinstance(v, list):
                    grouped[kl].extend([el for el in v if _is_row(el)])
    return grouped


def _group_obj(obj_node: Any) -> Dict[str, List[list] | List[dict]]:
    """
    Raggruppa fb/input/output/mot/alarm come liste di righe e PRESERVA i blocchi 'axis'
    (dict che contengono almeno la chiave 'axis' e tipicamente anche 'int','bool','type').
    Ritorna:
      {
        'fb': [...],
        'input': [...],
        'output': [...],
        'mot': [...],
        'alarm': [...],
        'maint': [...],
        'axis': [ { 'axis': [...], 'int': [...], 'bool': [...], 'type': [...] }, ... ]
      }
    """
    grouped: Dict[str, List[list] | List[dict]] = {
        'fb': [],
        'input': [],
        'output': [],
        'mot': [],
        'alarm': [],
        'axis': [],
        'maint': [],
    }

    def _is_row(x: Any) -> bool:
        return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            # Se è un blocco axis (ha la chiave 'axis'), lo conserviamo intero
            if 'axis' in node and isinstance(node.get('axis'), list):
                grouped['axis'].append(node)
            # Raggruppa chiavi note se in forma semplice
            for k, v in node.items():
                kl = str(k).lower()
                if kl in ('fb', 'input', 'output', 'mot', 'alarm', 'maint'):
                    if _is_row(v):
                        grouped[kl].append(v)  # es. {'fb': [ ...campi... ]}
                    elif isinstance(v, list):
                        grouped[kl].extend([el for el in v if _is_row(el)])  # es. {'fb': [[...],[...]]}
                # Scendi ricorsivamente per trovare altri blocchi/righe
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(obj_node)
    return grouped


def _pack_by_index(rows: List[list], idx_pos: int = 7) -> List[Optional[list]]:
    indexed: Dict[int, list] = {}
    extras: List[list] = []
    for r in rows:
        idx = r[idx_pos] if isinstance(r, list) and len(r) > idx_pos and isinstance(r[idx_pos], int) and r[
            idx_pos] >= 0 else None
        if idx is None:
            extras.append(r)
        elif idx not in indexed:
            indexed[idx] = r
        else:
            extras.append(r)
    if not indexed:
        return rows
    packed: List[Optional[list]] = [None] * (max(indexed.keys()) + 1)
    for i, r in indexed.items():
        packed[i] = r
    packed.extend(extras)
    return packed


def load_yaml(path: str) -> Any:
    logging.debug(f"📂 IN: load_yaml")
    """Carica e struttura il file YAML, con tentativi di correzione automatica e logging del metodo riuscito."""
    text = Path(path).read_text(encoding='utf-8')
    try:
        data = yaml.safe_load(text)
        logging.debug(f"✅ YAML caricato correttamente al primo tentativo: {path}")
    except yaml.YAMLError:
        logging.debug(f"⚠️ YAML non valido al primo parsing: → applico _sanitize_yaml_like()")
        text2 = _sanitize_yaml_like(text)
        try:
            data = yaml.safe_load(text2)
            logging.debug(f"✅ YAML caricato dopo _sanitize_yaml_like(): {path}")
        except yaml.YAMLError as e1:
            logging.debug(f"⚠️ Ancora errore dopo _sanitize_yaml_like(): {e1} → applico _sanitize_pstring_flow_lists()")
            text3 = _sanitize_pstring_flow_lists(text2)
            try:
                data = yaml.safe_load(text3)
                logging.debug(f"✅ YAML caricato dopo _sanitize_pstring_flow_lists(): {path}")
            except yaml.YAMLError as e2:
                logging.error(f"❌ Impossibile leggere il file YAML '{path}' anche dopo le sanificazioni: {e2}")
                raise RuntimeError("Config YAML non leggibile dopo i tentativi di sanificazione.") from e2

    # ---- Raggruppa IO ----
    io_grouped = _group_io(data.get('io'))
    for key, arr in io_grouped.items():
        if isinstance(arr, list):
            for i, row in enumerate(arr):
                if isinstance(row, list) and row:
                    if row[0] is None:
                        row[0] = ""
    data['io'] = io_grouped
    # ---- Raggruppa OBJ ----
    data['obj'] = _group_obj(data.get('obj'))
    logging.debug(f"📂 OUT: load_yaml")
    return data

