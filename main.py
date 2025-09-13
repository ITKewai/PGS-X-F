# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
from typing import Any, List, Tuple, Optional, Dict
from pathlib import Path
import yaml  # PyYAML

# Dipendenze per download non protetto
import requests
from urllib3.exceptions import InsecureRequestWarning  # type: ignore
import warnings as _warnings

"""
STRUTTURE:

- di: [NAME, BOOL_DEFAULT_VALUE, x, SIM, BOOL_SIM_VALUE, ADDRESS, CAMPO_1, CAMPO_2, x, UM, MEMTYPE, MEMIND, TIMEOUT, IN, x, x, x, x, x, EXPRTYPE,
     EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR,
     EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR,
     EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR,
     EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR,
     EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR,
     EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR,
     EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR]

(EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR) si attivano se EXPRTYPE != -1 se no non ci sono proprio
- io:
    - ai: [Free,0,0,0,0,-1,0,0,29,-1,-1,-1,-1,-1,55,77,22.222,0,33.333,4.44,-1]
    - ai: [NAME, BOOL_DEFAULT_VALUE, x, SIM, BOOL_SIM_VALUE, ADDRESS, CAMPO_1, CAMPO_2, NBYTES, UM, MEMTYPE, MEMIND, TIMEOUT, IN, DINTDEFAULTVALUE, DINTSIMVALUE, DEADBAND, x, TOTDELTAMAX, COEFFMULT, x]
    - ao: [NAME, BOOL_DEFAULT_VALUE, PROG, SIM, BOOL_SIM_VALUE, ADDRESS, CAMPO_1, CAMPO_2, NBYTES, UM, MEMTYPE, MEMIND, IN, AODUAL, DINTDEFAULTVALUE, DINTSIMVALUE, x, x, x, AOPRIORITY, x]
    - do: [NAME, BOOL_DEFAULT_VALUE, x, SIM, BOOL_SIM_VALUE, ADDRESS, CAMPO_1, CAMPO_2, x, UM, MEMTYPE, MEMIND, TIMEOUT, IN, x, x, x, x, x, x,x]

- obj:
    - fb: [FB_TYPE, FB_MESURETYPE, RESETIND, ININD, FB_ERR_DEPRECATED, INFUNDERFLOW, SUPOVERFLOW, DEADBAND, RATIO, x, x]
    - input: [HOLDTORUNENAB,x,INPUT_TYPE,INPUT_MESURETYPE, ANA, DIGUP1, DIGDOWN1, K, DIGUP2, DIGDOWN2, K2, ACT, ENAB1, ENAB2, ENAB3, SUP, SEQ, VMIN, VMAX, VMIN2, VMAX2]
    - output: [9,111,112,113,114,115,116,-1,-1,-1,117,118,119,120,121,122,123,124,125,126,127,128,129,130,143,144,131,137,132,138,133,139,134,140,135,141,136,142,145,151,146,152,147,153,148,154,149,155,150,156]
    - output: [5,111,112,113,114,115,116,117,-1,-1,-1,-1,-1,-1,121,122,123,124,125,126,127,128,129,130,143,144,131,137,132,138,133,139,134,140,135,141,136,142,145,151,146,152,147,153,148,154,149,155,150,156]
    - output: [OUTPUT_TYPE, ANA1, ANA2, DIG1, DIG2, CC, RPM, TIMEOUTBRKADV,ADVDEFSIDE,FREE,ACT,ENAB1,ENAB2,ENAB3, SCALEMIN1, SCALEMAX1, SCALEMIN2, SCALEMAX2, SCALEMIN1H, SCALEMAX1H, SCALEMIN2H, SCALEMAX2H, VALMIN1, VALMAX1, VALMIN2, VALMAX2, VIN0, VOUT0, VIN1, VOUT1, VIN2, VOUT2, VIN3, VOUT3, VIN4, VOUT4, VIN5, VOUT5, V2IN0, V2OUT0, V2IN1, V2OUT1, V2IN2, V2OUT2, V2IN3, V2OUT3, V2IN4, V2OUT4, V2IN5, V2OUT5] 
        se OUTPUT_TYPE = ADV
        ANA1 = ADVIND
        ANA2 = ADVSTART
        DIG1 = ADVENABLE
        DIG2 = BRAKE
        se OUTPUT_TYPE = PSLCAN
        RPM = CTRL1PSLCAN
        TIMEOUTBRKADV = STATUS1PSLCAN
        ADVDEFSIDE = CTRL2PSLCAN
        FREE = STATUS2PSLCAN  
        se OUTPUT_TYPE = ATV340
        RPM = RPMATV
        se OUTPUT_TYPE = SELSLOW
        ANA1 = DIG1ADD
        ANA2 = DIG2ADD
    - mot: [CONFIG, SELECTABLE, SEQ, OPT, DEFAULT, LSSTOP,LS2START, TR, CMD, STAT, TIMEOUT, CMD1, CMD2, CMD3, TIMEOUT2, MOT_TYPE, TIMEOUTBTN, TR2, STARTING]
    - axis: [NAME]
        bool: [x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x]
        int: ["x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","SUP","INF","x","x","x","x","x","x","x","x","x","x","ALTFBDIG","HH","H","L","LL","SAFETYUP1","SAFETYUP2","SAFETYUP3","SAFETYUP4","SAFETYUP5","SAFETYUP6","H0","L0","x","x","x","x","x","x","x","x","SAFETYDOWN1","SAFETYDOWN2","SAFETYDOWN3","SAFETYDOWN4","SAFETYDOWN5","SAFETYDOWN6","x","x","x","DECOUPLE1AUTO","DECOUPLE2MAN","DECOUPLE3MAN","DECOUPLE4MAN","DECOUPLE5MAN","DECOUPLE6MAN","PS1","x","x","PS2","PS3","x","x","x","x","x","FREE70","FREE71","x","x","x","x","x","x","x","BPDISABLE1","BPDISABLE2","BPDISABLE3","BPDISABLE4","BPDISABLE5","BPDISABLE6","BPDISABLE7","BPDISABLE8","BPDISABLE9","BPDISABLE10","BPDISABLE11","BPDISABLE12","OPTPARAM1","OPTPARAM2","OPTPARAM3"]
        type: [x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x]
    - in: [16,75,76,18,-1,-1,-1,-1,-1,95,-1,-1,12,13,-1,178,66,-1,70,-1,62,74,-1,-1,17,179,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,80,-1,-1,-1,86,81,114,-1,15,-1,-1,82,-1,-1,118,-1,-1,-1,84,-1,83,87,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,85,-1,98,97,-1,96,-1,68,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,69,101,-1,-1,-1,-1,2582,141,-1,-1,-1,-1,-1,-1,67,-1,-1,-1,-1,-1,39,-1,-1,-1,-1,-1,-1,-1]
    - in: [AUTOSEL,TEACHSEL,CYCLESEL,STARTRESET,-1,-1,-1,-1,-1,DEBALNOTPRESS,-1,-1,STARTIN,STOPIN,-1,HOLDTORUN,RTCOUPLED,-1,PINCHPRESS,-1,62,74,-1,-1,17,179,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,80,-1,-1,-1,86,81,114,-1,15,-1,-1,82,-1,-1,118,-1,-1,-1,84,-1,83,87,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,85,-1,98,97,-1,96,-1,68,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,69,101,-1,-1,-1,-1,2582,141,-1,-1,-1,-1,-1,-1,67,-1,-1,-1,-1,-1,39,-1,-1,-1,-1,-1,-1,-1]

"""

'''
NOTE: dentro gli -ao se tipo = PNET o CAN, trovo in IN e AO_DUAL gli -ai
'''
# --- Mappe fornite ---
ADDRESS = {
    -1: '',
    0: 'PNET',
    1: 'CAN',
    2: 'SW',
    3: 'CALC',
    4: 'TOT',
    5: 'TOTAUTO',
    6: 'TOTMAN',
    7: 'DAILYTOT',
    8: 'DAILYTOTAUTO',
    9: 'DAILYTOTMAN',
    10: 'TIME',
    11: 'TIMEAUTO',
    12: 'TIMEMAN',
    13: 'DAILYTIME',
    14: 'DAILYTIMEAUTO',
    15: 'DAILYTIMEMAN',
}

UM = {
    -1: '',
    0: 'LUNG',
    1: 'PRESS',
    2: 'TEMP',
    3: 'VEL',
    4: 'YP',
    5: 'RAPP',
    6: 'VELASS',
    7: 'VELPRESS',
    8: 'AREA',
    9: 'ROT',
    10: 'E0',
    11: 'GRAD',
    12: 'NUM',
}

MEMTYPE = {
    -1: '',
    0: '',
    1: '',
    2: '',
    3: 'EVENTS',
    4: 'INT',
    5: 'REAL',
}

FB_TYPE = {
    -1: '',
    1: 'AI',
    2: 'DI',
    3: 'RHSC',
    4: 'AHSC',
    5: 'ATV340',
    6: 'INC',
    7: 'AI2',
}

FB_MESURETYPE = UM.copy()

# SOLO SE ADDRESS >= 4
CAMPO_1 = {
    -1: '',
    0: 'DI',
    1: 'AI',
    2: 'DO',
    3: 'AO',
    4: 'RI',
}

EXPRTYPE = {
    -1: '',
    0: 'CYCLE',
    1: 'TRIGGER',
}

INPUT_MESURETYPE = UM.copy()

OUTPUT_TYPE = {
    -1: '',
    0: 'SEL',
    1: 'DIR',
    2: 'DIRINV',
    3: 'SELSLOW',
    4: 'ADV',
    5: 'PSLCAN',
    6: 'SELFL',
    7: 'SEL2PV',
    8: 'ATV340',
}

MOT_TYPE = {
    -1: '',
    0: 'M1',
    1: 'M2',
    2: 'M3',
    3: 'M4',
    4: 'M5',
    5: 'M6',
    6: 'M7',
    7: 'M8',
    8: 'Recycling',
    9: 'Cooling',
    10: 'Heating',
    11: 'RT',
    12: 'RT2',
    13: 'Flushing',
}
# SOLO SE ADDRESS == 4 SI ABILITANO I CAMPI TIMEOUT E IN
# EXPR_ADDRESS: intero "grezzo" (senza mappa)

EXPR_OPERAND = {
    -1: '-',
    0: '',
    1: 'NOT',
    2: 'AI == 0',
    3: 'AI != 0',
    4: 'AI > 0',
    5: 'AI >= 0',
    6: 'AI < 0',
    7: 'AI <= 0',
    8: 'RI == 0',
    9: 'RI != 0',
    10: 'RI > 0',
    11: 'RI >= 0',
    12: 'RI < 0',
    13: 'RI <= 0',
}

EXPR_OPERAND_DI = [-1, 0, 1]
EXPR_OPERAND_AI = [2, 3, 4, 5, 6, 7]
EXPR_OPERAND_RI = [8, 9, 10, 11, 12, 13]

EXPR_OPERATOR = {
    -1: '-',
    0: 'AND',
    1: 'OR',
}

AO_PRIORITY = {
    -1: 'FIRST',
    0: 'MIN'
}

# --- Indici attesi nella struttura obj>input ---
IDX_EXPRTYPE = 20
IDX_DI_IN = 13
IDX_AO_ADDRESS = 5
IDX_AO_IN = 12
IDX_AO_DUAL = 13
IDX_DO_IN = 13
IDX_FB_TYPE = 0
IDX_FB_RESETIND = 2
IDX_FB_ERR_DEPRECATED = 4
DI_NUM_EXPR_GROUPS = 8
DI_EXPR_GROUP_SIZE = 3  # (EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR)
IDX_INPUT_DIGUP1 = 5
IDX_INPUT_DIGDOWN1 = 6
IDX_INPUT_DIGUP2 = 8
IDX_INPUT_DIGDOWN2 = 9
IDX_INPUT_ACT = 11
IDX_INPUT_ENAB1 = 12
IDX_INPUT_ENAB2 = 13
IDX_INPUT_ENAB3 = 14
IDX_OUTPUT_TYPE = 0
IDX_OUTPUT_ANA1 = 1
IDX_OUTPUT_ANA2 = 2
IDX_OUTPUT_ACT = 10
IDX_OUTPUT_ENAB1 = 11
IDX_OUTPUT_ENAB2 = 12
IDX_OUTPUT_ENAB3 = 13
IDX_MOT_LSSTOP = 5
IDX_MOT_LS2START = 6
IDX_MOT_TR = 7
IDX_MOT_STAT = 9
IDX_MOT_TR2 = 17
IDX_MOT_STARTING = 18
AXIS_INT_INDEXES: Dict[str, int] = {
    "SUP": 19,
    "INF": 20,
    "ALTFBDIG": 31,
    "HH": 32,
    "H": 33,
    "L": 34,
    "LL": 35,
    "SAFETYUP1": 36,
    "SAFETYUP2": 37,
    "SAFETYUP3": 38,
    "SAFETYUP4": 39,
    "SAFETYUP5": 40,
    "SAFETYUP6": 41,
    "H0": 42,
    "L0": 43,
    # "INDMEM": 44,
    "SAFETYDOWN1": 48,
    "SAFETYDOWN2": 49,
    "SAFETYDOWN3": 50,
    "SAFETYDOWN4": 51,
    "SAFETYDOWN5": 52,
    "SAFETYDOWN6": 53,
    "DECOUPLE1AUTO": 57,
    "DECOUPLE2MAN": 58,
    "DECOUPLE3MAN": 59,
    "DECOUPLE4MAN": 60,
    "DECOUPLE5MAN": 61,
    "DECOUPLE6MAN": 62,
    "FREE70": 70,
    "FREE71": 71,
    "BPDISABLE1": 76,
    "BPDISABLE2": 77,
    "BPDISABLE3": 78,
    "BPDISABLE4": 79,
    "BPDISABLE5": 80,
    "BPDISABLE6": 81,
    "BPDISABLE7": 82,
    "BPDISABLE8": 83,
    "BPDISABLE9": 84,
    "BPDISABLE10": 85,
    "BPDISABLE11": 86,
    "BPDISABLE12": 87,
    "OPTPARAM1": 88,
    "OPTPARAM2": 89,
    "OPTPARAM3": 90,
    "PS1": 63,
    "PS2": 66,
    "PS3": 67,
}


def _sanitize_yaml_like(text: str) -> str:
    """
    Converte sequenze in stile YAML con elementi vuoti/trailing comma in 'null'.
    Esempi:
      [a, b,,]   -> [a, b, null, null]
      [,a,,b,]   -> [null, a, null, b, null]
    NOTE: approccio best-effort basato su regex; pensato per casi reali del file.
    """
    import re
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r',\s*,', ', null,', text)  # elemento vuoto tra due virgole
    text = re.sub(r'\[\s*,', '[ null,', text)  # vuoto subito dopo '['
    text = re.sub(r',\s*\]', ', null]', text)  # vuoto prima di ']'
    return text


def load_yaml(path: str) -> Any:
    text = Path(path).read_text(encoding='utf-8')
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        text2 = _sanitize_yaml_like(text)
        try:
            data = yaml.safe_load(text2)
        except yaml.YAMLError as e1:
            text3 = _sanitize_pstring_flow_lists(text2)
            try:
                data = yaml.safe_load(text3)
            except yaml.YAMLError as e2:
                raise RuntimeError("Config YAML non leggibile dopo i tentativi di sanificazione.") from e2

    # ---- raggruppa IO e impacchetta i DI per indice di canale ----
    io_grouped = _group_io(data.get('io'))
    io_grouped['di'] = _pack_by_index(io_grouped.get('di', []), idx_pos=7)
    data['io'] = io_grouped
    # Raggruppa gli oggetti (fb) sotto 'obj'
    obj_grouped = _group_obj(data.get('obj'))
    data['obj'] = obj_grouped
    return data


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


def _group_io(io_node: Any, keys=('di', 'ai', 'do', 'ao', 'ri', 'fb')) -> Dict[str, List[list]]:
    grouped: Dict[str, List[list]] = {k: [] for k in keys}

    def _is_row(x: Any) -> bool:
        return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)

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
    Raggruppa fb/input/output/mot come prima e in più PRESERVA i blocchi 'axis'
    (dict che contengono almeno la chiave 'axis' e tipicamente anche 'int','bool','type').
    Ritorna:
      {
        'fb': [...],
        'input': [...],
        'output': [...],
        'mot': [...],
        'axis': [ { 'axis': [...], 'int': [...], 'bool': [...], 'type': [...] }, ... ]
      }
    """
    grouped: Dict[str, List[list] | List[dict]] = {
        'fb': [],
        'input': [],
        'output': [],
        'mot': [],
        'axis': [],  # <--- NOVITÀ: conserviamo i blocchi axis interi
    }

    def _is_row(x: Any) -> bool:
        return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            # Se è un blocco axis (ha la chiave 'axis'), lo conserviamo intero
            if 'axis' in node and isinstance(node.get('axis'), list):
                grouped['axis'].append(node)
                # Continuiamo comunque a scendere per catturare eventuali fb/input annidati
            # Raggruppa chiavi note se in forma semplice
            for k, v in node.items():
                kl = str(k).lower()
                if kl in ('fb', 'input', 'output', 'mot'):
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


def find_section(root: Any, keys: List[str]) -> Optional[List[list]]:
    """
    Cerca ricorsivamente tutte le occorrenze di chiavi in `keys` (case-insensitive)
    in qualunque punto della struttura (dict o list). Ogni valore trovato che sia
    una LISTA 'riga' (es. un singolo DI) viene aggiunto al risultato.
    Se il valore è una lista di liste, le appiattisce.
    Restituisce una lista di liste oppure None se non trova nulla.
    """
    targets = {k.lower() for k in keys}
    found: List[list] = []

    def is_row(x: Any) -> bool:
        # una "riga" è una lista i cui elementi NON sono dict/list annidati
        return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                # se la chiave è tra quelle cercate, prova a raccogliere il valore
                if k.lower() in targets:
                    if is_row(v):
                        found.append(v)  # es. {'di': [ ... campi ... ]}
                    elif isinstance(v, list):
                        # potrebbe essere una lista di righe: [[...],[...],...]
                        rows = [list(el) for el in v if is_row(el)]
                        if rows:
                            found.extend(rows)
                # continua a scendere comunque
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(root)
    return found or None


def _find_axis_int_lists(root: Any) -> List[List[Any]]:
    """
    Ritorna tutte le liste 'int' appartenenti a nodi 'axis'.
    Un nodo 'axis' è un dict che contiene la chiave 'axis' (es. 'axis': [NAME])
    e a fianco una chiave 'int' che è una lista di interi.
    """
    axis_ints: List[List[Any]] = []

    def walk(node: Any, under_axis: bool = False) -> None:
        if isinstance(node, dict):
            # un livello è "axis" se ha la chiave 'axis' (come da struttura mostrata)
            is_axis_here = under_axis or ('axis' in node and isinstance(node.get('axis'), list))
            # se siamo su un livello axis e troviamo 'int' come lista, raccogliamo
            if is_axis_here and isinstance(node.get('int'), list):
                axis_ints.append(node['int'])
            # continua discesa
            for k, v in node.items():
                walk(v, under_axis=is_axis_here or (k == 'axis'))
        elif isinstance(node, list):
            for item in node:
                walk(item, under_axis=under_axis)

    walk(root, under_axis=False)
    return axis_ints


def iter_expr_groups(di_fields: list) -> List[Tuple[int, int, int]]:
    groups: List[Tuple[int, int, int]] = []
    if not isinstance(di_fields, list) or len(di_fields) <= IDX_EXPRTYPE:
        return groups
    # EXPRTYPE è a indice 20; le terne partono da 21 → (operand, address, operator)
    start = IDX_EXPRTYPE + 1
    max_needed = start + DI_NUM_EXPR_GROUPS * DI_EXPR_GROUP_SIZE
    limit = min(len(di_fields), max_needed)
    i = start
    while i + 2 < limit and len(groups) < DI_NUM_EXPR_GROUPS:
        try:
            operand = int(di_fields[i])
        except:
            operand = -999999
        try:
            address = int(di_fields[i + 1])
        except:
            address = -999999
        try:
            operator = int(di_fields[i + 2])
        except:
            operator = -999999
        groups.append((operand, address, operator))  # (OPERAND, ADDRESS, OPERATOR)
        i += DI_EXPR_GROUP_SIZE
    return groups


def search_di_matches(di_list: List[list], target_number: int) -> List[Tuple[int, str, int]]:
    results: List[Tuple[int, str, int]] = []
    for di_index, di_fields in enumerate(di_list):
        if not isinstance(di_fields, list):
            continue
        if len(di_fields) > IDX_EXPRTYPE:
            try:
                exprtype_val = int(di_fields[IDX_EXPRTYPE])
            except Exception:
                exprtype_val = -1
        else:
            exprtype_val = -1
        exprtype_str = EXPRTYPE.get(exprtype_val, str(exprtype_val))
        groups = iter_expr_groups(di_fields)
        for g_idx, (operand, address, operator) in enumerate(groups):
            if operand in EXPR_OPERAND_DI and address == target_number:
                results.append((di_index, exprtype_str, g_idx))
    return results


def search_di_in_matches(di_list: List[list], target_number: int) -> List[Tuple[int, str]]:
    """
    Cerca tutti i DI che hanno il campo IN (indice 13) uguale a target_number.
    Ritorna una lista di indici di DI.
    """
    results: List[int] = []
    for di_index, di_fields in enumerate(di_list):
        if not isinstance(di_fields, list) or len(di_fields) <= IDX_DI_IN:
            continue
        try:
            in_val = int(di_fields[IDX_DI_IN])
        except Exception:
            continue
        if in_val == target_number:
            results.append(di_index)
    return results


def search_ai_in_ao_matches(ao_list: List[list], target_number: int, only_bus: bool = True) -> List[
    Tuple[int, str, Optional[str]]]:
    """
    Cerca tutti gli AO che referenziano l'AI `target_number` in IN o AODUAL.
    Se only_bus=True, considera solo AO con ADDRESS PNET(0) o CAN(1).
    Ritorna: [(indice_ao, 'IN'|'AODUAL', nome_ao_opzionale)]
    """
    matches: List[Tuple[int, str, Optional[str]]] = []
    for ao_index, ao_fields in enumerate(ao_list or []):
        if not isinstance(ao_fields, list):
            continue

        # Filtra per bus PNET/CAN se richiesto
        addr_val = None
        if len(ao_fields) > IDX_AO_ADDRESS:
            try:
                addr_val = int(ao_fields[IDX_AO_ADDRESS])
            except Exception:
                addr_val = None
        if only_bus and addr_val not in (0, 1):  # 0=PNET, 1=CAN
            continue

        name = None
        if len(ao_fields) > 0 and isinstance(ao_fields[0], (str, int, float)):
            name = str(ao_fields[0])

        # Controlla i campi IN e AODUAL
        for label, idx in (("IN", IDX_AO_IN), ("AODUAL", IDX_AO_DUAL)):
            if len(ao_fields) > idx:
                try:
                    val = int(ao_fields[idx])
                except Exception:
                    continue
                if val == target_number:
                    matches.append((ao_index, label, name))
    return matches


def search_do_in_matches(do_list: List[list], target_number: int) -> List[Tuple[int, Optional[str]]]:
    """
    Cerca tutti i DO che hanno il campo IN (indice 13) uguale a target_number.
    Ritorna: [(indice_do, nome_do_opzionale)]
    """
    results: List[Tuple[int, Optional[str]]] = []
    for do_index, do_fields in enumerate(do_list or []):
        if not isinstance(do_fields, list) or len(do_fields) <= IDX_DO_IN:
            continue
        try:
            in_val = int(do_fields[IDX_DO_IN])
        except Exception:
            continue
        if in_val == target_number:
            name: Optional[str] = None
            if len(do_fields) > 0 and isinstance(do_fields[0], (str, int, float)):
                name = str(do_fields[0])
            results.append((do_index, name))
    return results


def search_fb_err_deprecated_matches(fb_list: List[list], target_number: int) -> List[Tuple[int, Optional[str]]]:
    """
    Cerca tutti i FB che hanno il campo FB_ERR_DEPRECATED (indice 4) uguale a target_number.
    Ritorna: [(indice_fb, fb_type_string_opzionale)]
    """
    results: List[Tuple[int, Optional[str]]] = []
    for fb_index, fb_fields in enumerate(fb_list or []):
        if not isinstance(fb_fields, list) or len(fb_fields) <= IDX_FB_ERR_DEPRECATED:
            continue
        try:
            err_val = int(fb_fields[IDX_FB_ERR_DEPRECATED])
        except Exception:
            continue
        if err_val == target_number:
            fb_type_str: Optional[str] = None
            if len(fb_fields) > IDX_FB_TYPE:
                try:
                    fb_type_val = int(fb_fields[IDX_FB_TYPE])
                except Exception:
                    fb_type_val = -1
                fb_type_str = FB_TYPE.get(fb_type_val, str(fb_type_val))
            results.append((fb_index, fb_type_str))
    return results


def search_fb_resetind_matches(fb_list: List[list], target_number: int) -> List[Tuple[int, Optional[str]]]:
    """
    Cerca tutti i FB che hanno il campo RESETIND (indice 2) uguale a target_number.
    Ritorna: [(indice_fb, fb_type_string_opzionale)]
    """
    results: List[Tuple[int, Optional[str]]] = []
    for fb_index, fb_fields in enumerate(fb_list or []):
        if not isinstance(fb_fields, list) or len(fb_fields) <= IDX_FB_RESETIND:
            continue
        try:
            reset_val = int(fb_fields[IDX_FB_RESETIND])
        except Exception:
            continue
        if reset_val == target_number:
            fb_type_str: Optional[str] = None
            if len(fb_fields) > IDX_FB_TYPE:
                try:
                    fb_type_val = int(fb_fields[IDX_FB_TYPE])
                except Exception:
                    fb_type_val = -1
                fb_type_str = FB_TYPE.get(fb_type_val, str(fb_type_val))
            results.append((fb_index, fb_type_str))
    return results


def search_input_di_field_matches(input_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in obj>input i campi DIGUP1, DIGDOWN1, DIGUP2, DIGDOWN2, ENAB1, ENAB2, ENAB3
    che referenziano il DI `target_number`.
    Ritorna: [(indice_input, [nomi_campi_match])]
    """
    results: List[Tuple[int, List[str]]] = []
    fields = [
        ("DIGUP1", IDX_INPUT_DIGUP1),
        ("DIGDOWN1", IDX_INPUT_DIGDOWN1),
        ("DIGUP2", IDX_INPUT_DIGUP2),
        ("DIGDOWN2", IDX_INPUT_DIGDOWN2),
        ("ACT", IDX_INPUT_ACT),
        ("ENAB1", IDX_INPUT_ENAB1),
        ("ENAB2", IDX_INPUT_ENAB2),
        ("ENAB3", IDX_INPUT_ENAB3),
    ]
    for inp_index, inp_fields in enumerate(input_list or []):
        if not isinstance(inp_fields, list):
            continue
        matched: List[str] = []
        for label, idx in fields:
            if len(inp_fields) > idx:
                try:
                    val = int(inp_fields[idx])
                except Exception:
                    continue
                if val == target_number:
                    matched.append(label)
        if matched:
            results.append((inp_index, matched))
    return results


def search_output_di_field_matches(output_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in obj>output SOLO i campi ACT, ENAB1, ENAB2, ENAB3 che referenziano il DI `target_number`.
    Ritorna: [(indice_output, [nomi_campi_match])]
    """
    results: List[Tuple[int, List[str]]] = []
    for out_index, out_fields in enumerate(output_list or []):
        if not isinstance(out_fields, list):
            continue

        matched: List[str] = []
        field_specs = [
            ("ACT", IDX_OUTPUT_ACT),
            ("ENAB1", IDX_OUTPUT_ENAB1),
            ("ENAB2", IDX_OUTPUT_ENAB2),
            ("ENAB3", IDX_OUTPUT_ENAB3),
        ]

        for label, idx in field_specs:
            if len(out_fields) > idx:
                try:
                    val = int(out_fields[idx])
                except Exception:
                    continue
                if val == target_number:
                    matched.append(label)

        if matched:
            results.append((out_index, matched))

    return results


def search_mot_di_field_matches(mot_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in obj>mot i campi LSSTOP, LS2START, TR, STAT, TR2, STARTING
    che referenziano il DI `target_number`.
    Ritorna: [(indice_mot, [nomi_campi_match])]
    """
    results: List[Tuple[int, List[str]]] = []
    field_specs = [
        ("LSSTOP", IDX_MOT_LSSTOP),
        ("LS2START", IDX_MOT_LS2START),
        ("TR", IDX_MOT_TR),
        ("STAT", IDX_MOT_STAT),
        ("TR2", IDX_MOT_TR2),  # "T2"
        ("STARTING", IDX_MOT_STARTING),
    ]

    for mot_index, mot_fields in enumerate(mot_list or []):
        if not isinstance(mot_fields, list):
            continue
        matched: List[str] = []
        for label, idx in field_specs:
            if len(mot_fields) > idx:
                try:
                    val = int(mot_fields[idx])
                except Exception:
                    continue
                if val == target_number:
                    matched.append(label)
        if matched:
            results.append((mot_index, matched))

    return results


def search_axis_int_di_field_matches(axis_int_lists: List[List[Any]], target_number: int) -> List[
    Tuple[int, List[str]]]:
    """
    Cerca in ciascun array 'axis.int' i campi etichettati (SUP, INF, ALTFBDIG, HH, H, L, LL,
    SAFETYUP1..6, H0, L0, INDMEM, SAFETYDOWN1..6, DECOUPLE1AUTO..6, FREE70, FREE71,
    BPDISABLE1..12 (incl. BPDISABL7), OPTPARAM1..3) che referenziano il DI 'target_number'.
    Ritorna: [(indice_axis, [nomi_campi_match])]
    """
    results: List[Tuple[int, List[str]]] = []
    for axis_idx, arr in enumerate(axis_int_lists or []):
        if not isinstance(arr, list):
            continue
        matched: List[str] = []
        for label, idx in AXIS_INT_INDEXES.items():
            if idx < 0:
                continue
            if idx >= len(arr):
                continue
            try:
                val = int(arr[idx])
            except Exception:
                continue
            if val == target_number:
                matched.append(label)
        if matched:
            results.append((axis_idx, matched))
    return results


def _build_download_url(addr: str) -> str:
    """
    Costruisce l'URL finale a partire da un input tipo:
      - 10.3.73.177
      - http://10.3.73.177
      - https://10.3.73.177
      - https://10.3.73.177/UserFiles?Name=config.yaml&Action=DOWNLOAD
    Se l'input NON contiene '://', assume https://<addr> + path fisso richiesto.
    """
    addr = addr.strip()
    path = '/UserFiles?Name=config.yaml&Action=DOWNLOAD'
    if '://' in addr:
        # Se l'utente ha già messo il path completo, lo usiamo com'è.
        if '?' in addr or addr.endswith('/UserFiles') or '/UserFiles' in addr:
            return addr
        # Altrimenti aggiungiamo il path richiesto
        return addr.rstrip('/') + path
    # Default: https
    return f'https://{addr}{path}'


def download_file(url: str, dest_path: Path) -> None:
    """
    Scarica il file dall'URL fornito e lo salva in dest_path.
    Connessione NON protetta (verify=False). Se HTTPS fallisce, tenta HTTP.
    """
    print('Download in corso... (connessione non protetta / certificato non verificato)')
    try:
        _warnings.simplefilter('ignore', InsecureRequestWarning)  # sopprimi warning
    except Exception:
        pass

    try:
        r = requests.get(url, timeout=60, verify=False)
        r.raise_for_status()
        dest_path.write_bytes(r.content)
    except Exception as e_https:
        # Fallback a HTTP se l'URL era https://<host>/...
        try:
            if url.startswith('https://'):
                url_http = 'http://' + url[len('https://'):]
                r = requests.get(url_http, timeout=60)
                r.raise_for_status()
                dest_path.write_bytes(r.content)
            else:
                raise
        except Exception as e_http:
            raise RuntimeError(f'Errore nel download.\nHTTPS: {e_https}\nHTTP: {e_http}') from e_http

    print(f'File salvato in: {dest_path}')


def choose_and_prepare_config() -> Path:
    """
    Chiede se usare file locale o scaricare da internet.
    Ritorna il Path del file pronto da leggere.
    """
    script_dir = Path(__file__).resolve().parent
    print("Selezione sorgente file 'config.yaml'")
    print("  [1] Usa file locale (stessa cartella dello script)")
    print("  [2] Scarica da internet e sovrascrivi il file locale (connessione NON protetta)")
    choice = input("Scelta: ").strip().upper()

    try:
        choice = int(choice)
    except ValueError:
        print(f"Opzione non valida")
        sys.exit(1)

    if choice == 'D':
        base = input("Inserisci indirizzo/IP (es: 10.3.73.177 oppure https://10.3.73.177): ").strip()
        if not base:
            print("Indirizzo non valido.")
            sys.exit(1)
        url = _build_download_url(base)
        dest = script_dir / "config.yaml"
        try:
            download_file(url, dest)
        except Exception as e:
            print(f"Errore nel download: {e}")
            sys.exit(1)
        return dest

    # Locale
    path = script_dir / "config.yaml"
    if not path.exists():
        print(f"File locale non trovato: {path}")
        sys.exit(1)
    return path


def main():
    cfg_path = choose_and_prepare_config()

    try:
        data = load_yaml(str(cfg_path))
    except Exception as e:
        print(f"Errore nel parsing YAML: {e}")
        sys.exit(1)

    tipo = input("Che tipo stai cercando? (1=DI, 2=AI, 3=DO, 4=AO): ").strip()
    try:
        tipo = int(tipo)
    except ValueError:
        sys.exit(1)
    if tipo not in range(1, 5):
        print("Tipo non valido. Usa 'DI', 'AI', 'DO' o 'AO'.")
        sys.exit(1)
    try:
        target_str = input("Inserisci il numero da cercare: ").strip()
        target_number = int(target_str)
    except ValueError:
        print("Numero non valido.")
        sys.exit(1)

    if tipo == 1:
        di_list = (data.get('io') or {}).get('di')  # <-- lista indicizzata
        if not di_list:
            print("Sezione 'di' non trovata.")
            sys.exit(1)
        # ricerca nelle espressioni dei -di
        matches = search_di_matches(di_list, target_number)
        if matches:
            for di_idx, exprtype_str, group_idx in matches:
                print(f"IO>DI>{di_idx} - {exprtype_str} - EXPRESSION N°{group_idx}")

        # ricerca nel campo IN dei -di (il campo si vede su HMI se messo come tipo CALC)
        in_matches = search_di_in_matches(di_list, target_number)
        for di_idx in in_matches:
            print(f"IO>DI>{di_idx} - IN match")
        # ricerca nel campo IN dei -do
        do_list = (data.get('io') or {}).get('do')
        if do_list:
            do_matches = search_do_in_matches(do_list, target_number)
            for do_idx, name in do_matches:
                if name:
                    print(f"IO>DO>{do_idx} - IN match (-do) - DO name: {name}")
                else:
                    print(f"IO>DO>{do_idx} - IN match (-do)")
        # ricerca nel campo FB_ERR_DEPRECATED dei -fb
        fb_list = (data.get('obj') or {}).get('fb')
        if fb_list:
            fb_matches = search_fb_err_deprecated_matches(fb_list, target_number)
            for fb_idx, fb_type in fb_matches:
                if fb_type:
                    print(f"FEEDBACK>{fb_idx} - FB_ERR_DEPRECATED match (-fb)")
                else:
                    print(f"FEEDBACK>{fb_idx} - FB_ERR_DEPRECATED match (-fb)")
        # ricerca nel campo RESETIND dei -fb
        if fb_list:
            fb_reset_matches = search_fb_resetind_matches(fb_list, target_number)
            for fb_idx, fb_type in fb_reset_matches:
                if fb_type:
                    print(f"FEEDBACK>{fb_idx} - RESETIND match (-fb)")
                else:
                    print(f"FEEDBACK>{fb_idx} - RESETIND match (-fb)")
        # ricerca nei campi DIGUP*/DIGDOWN*/ENAB*/ACT dei -input
        input_list = (data.get('obj') or {}).get('input')
        if input_list:
            in_input_matches = search_input_di_field_matches(input_list, target_number)
            for inp_idx, fields in in_input_matches:
                print(f"INPUT>{inp_idx} - match (-input) - fields: {', '.join(fields)}")
        # ricerca nei campi ACT/ENAB* dei -output
        output_list = (data.get('obj') or {}).get('output')
        if output_list:
            out_matches = search_output_di_field_matches(output_list, target_number)
            for out_idx, fields in out_matches:
                print(f"OUTPUT>{out_idx} - match (-output) - fields: {', '.join(fields)}")
        # ricerca nei campi LSSTOP, LS2START, TR, STAT, TR2, STARTING dei -mot
        mot_list = (data.get('obj') or {}).get('mot')
        if mot_list:
            mot_matches = search_mot_di_field_matches(mot_list, target_number)
            for mot_idx, fields in mot_matches:
                print(f"MOT>{mot_idx} - match (-mot) - fields: {', '.join(fields)}")
        # ricerca nei campi etichettati dell’array -axis.int
        axis_int_lists = _find_axis_int_lists(data.get('obj'))
        if axis_int_lists:
            axis_matches = search_axis_int_di_field_matches(axis_int_lists, target_number)
            for axis_idx, fields in axis_matches:
                print(f"AXIS>{axis_idx} - match (-axis.int) - fields: {', '.join(fields)}")
    elif tipo == 2:
        # Ricerca AI negli AO (IN/AODUAL)
        ao_list = (data.get('io') or {}).get('ao')
        if ao_list:
            matches = search_ai_in_ao_matches(ao_list, target_number, only_bus=True)
            if matches:
                for ao_idx, where, name in matches:
                    if name:
                        print(f"{ao_idx} - {where} match - AO name: {name}")
                    else:
                        print(f"{ao_idx} - {where} match")
        # ricerca nel campo ANA SUP dei -input
        # elif tipo == 4:
        # RICERCA NEL CAMPO DEI -fb
        # TODO: se tipo fb è AI o AI2 va cercato in ININD

        sys.exit(0)
    else:
        print(f"Ricerca per '{tipo}' non ancora implementata. Al momento è attiva solo la ricerca nei 'DI'.")
        sys.exit(0)


if __name__ == "__main__":
    main()
