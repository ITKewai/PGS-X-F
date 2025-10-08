#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
from typing import Any, List, Tuple, Optional, Dict
from pathlib import Path
import yaml  # PyYAML
import requests
from urllib3.exceptions import InsecureRequestWarning
import warnings as _warnings
from utils.yaml.data.costants import *
from utils.yaml.data.humanize import *
from utils.yaml.download import choose_and_prepare_config, fetch_again
from utils.yaml.load import load_yaml

# from utils.version import __version__, __pgs_version__, __author__, __company__, __product__, __copyright__

# TODO: download config con salvataggio versione data
# TODO: tasterino numerico tipo touch per fare interazioni


def key_for_value(d, value):
    for k, v in d.items():
        if v == value:
            return k
    raise KeyError(f"Value {value!r} not found")


# ---- Funzioni AXIS ----
def make_axis_sys_addr(group: str, axis_index: int) -> int:
    g = group.strip().upper()
    if g not in AXIS_GROUP_BASE:
        raise KeyError(f"Gruppo AXIS sconosciuto: {group}")
    if not (0 <= axis_index <= AXIS_MAX_INDEX):  # 0..47
        raise ValueError(f"axis_index fuori range (0..{AXIS_MAX_INDEX}): {axis_index}")
    return AXIS_GROUP_BASE[g] + axis_index


def parse_axis_sys_addr(addr: int) -> Optional[Tuple[str, int]]:
    if addr < 2048 or addr >= 2048 + AXIS_GROUP_STEP * len(AXIS_GROUPS_ORDER):
        return None
    group_idx = (addr - 2048) // AXIS_GROUP_STEP
    if not (0 <= group_idx < len(AXIS_GROUPS_ORDER)):
        return None
    base = 2048 + group_idx * AXIS_GROUP_STEP
    axis_index = addr - base
    if not (0 <= axis_index <= AXIS_MAX_INDEX):  # 0..47
        return None
    return AXIS_GROUPS_ORDER[group_idx], axis_index


def make_alarm_sys_addr(group: str, alarm_index: int) -> int:
    g = group.strip().upper()
    if g not in ALARM_GROUP_BASE:
        raise KeyError(f"Gruppo ALARM sconosciuto: {group}")
    if not (0 <= alarm_index <= ALARM_MAX_INDEX):  # 0..191
        raise ValueError(f"alarm_index fuori range (0..{ALARM_MAX_INDEX}): {alarm_index}")
    return ALARM_GROUP_BASE[g] + alarm_index


def parse_alarm_sys_addr(addr: int) -> Optional[Tuple[str, int]]:
    if addr < 16384 or addr >= 16384 + ALARM_GROUP_STEP * len(ALARM_GROUPS_ORDER):
        return None
    group_idx = (addr - 16384) // ALARM_GROUP_STEP
    if not (0 <= group_idx < len(ALARM_GROUPS_ORDER)):
        return None
    base = 16384 + group_idx * ALARM_GROUP_STEP
    alarm_index = addr - base
    if not (0 <= alarm_index <= ALARM_MAX_INDEX):  # 0..191
        return None
    return ALARM_GROUPS_ORDER[group_idx], alarm_index


# ---- Decoder generale (AXIS / ALARM; altri tipi in futuro) ----
def decode_system_addr(addr: int) -> Optional[str]:
    """
    Prova a decodificare un indirizzo di sistema in forma umana.
    Ritorna stringa tipo 'AXIS.MOVING[3]' oppure 'ALARM.ACK[12]' oppure None.
    """
    ax = parse_axis_sys_addr(addr)
    if ax:
        g, i = ax
        return f"AXIS.{g}[{i}]"
    al = parse_alarm_sys_addr(addr)
    if al:
        g, i = al
        return f"ALARM.{g}[{i}]"
    return None


def validate_system_index(sys_type: str, index: int) -> None:
    """Lancia ValueError se l'indice non rientra nei limiti dichiarati per il tipo."""
    t = sys_type.strip().upper()
    if t in {"AXIS", "INPUT", "OUTPUT", "FEEDBACK", "AXISREAL"}:
        if not (0 <= index <= AXIS_MAX_INDEX):
            raise ValueError(f"{t} index fuori range (0..{AXIS_MAX_INDEX}): {index}")
    elif t == "MOTOR":
        if not (MOTOR_MIN_INDEX <= index <= MOTOR_MAX_INDEX):
            raise ValueError(f"MOTOR index fuori range ({MOTOR_MIN_INDEX}..{MOTOR_MAX_INDEX}): {index}")
    elif t == "TOOLSET":
        if not (0 <= index <= TOOLSET_MAX_INDEX):
            raise ValueError(f"TOOLSET index fuori range (0..{TOOLSET_MAX_INDEX}): {index}")
    elif t == "ALARM":
        if not (0 <= index <= ALARM_MAX_INDEX):
            raise ValueError(f"ALARM index fuori range (0..{ALARM_MAX_INDEX}): {index}")
    elif t == "MAINT":
        if not (0 <= index <= MAINT_MAX_INDEX):
            raise ValueError(f"MAINT index fuori range (0..{MAINT_MAX_INDEX}): {index}")
    else:
        raise ValueError(f"Tipo di sistema sconosciuto: {sys_type}")


def sysref(sys_type: str, field: str, index: int) -> str:
    """
    Ritorna una stringa tipo 'AXIS.MOVING[3]' o 'ALARM.ACK[12]'.
    Per gli altri tipi valida il range e usa lo stesso formato 'TIPO.CAMPO[idx]'.
    """
    t = sys_type.strip().upper()
    f = field.strip().upper()
    validate_system_index(t, index)

    if t == "AXIS":
        if f not in AXIS_GROUP_BASE:
            raise KeyError(f"Campo AXIS sconosciuto: {field}")
        return f"AXIS.{f}[{index}]"

    if t == "ALARM":
        if f not in ALARM_GROUP_BASE:
            raise KeyError(f"Campo ALARM sconosciuto: {field}")
        return f"ALARM.{f}[{index}]"

    # altri tipi (INPUT/OUTPUT/FEEDBACK/MOTOR/TOOLSET/MAINT/AXISREAL)
    return f"{t}.{f}[{index}]"


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


def get_sn_from_param(data: Any) -> Optional[str]:
    """
    Ritorna la stringa della sn da param.pint[0], se presente.
    Supporta sia:
      - param: { pint: [...] }
      - param: [ { pint: [...] }, ... ]
    """
    if not isinstance(data, dict):
        return None
    param = data.get('param')

    # Caso 1: param è un dict con chiave 'pint'
    if isinstance(param, dict) and isinstance(param.get('pint'), list):
        row = param['pint']
        if row and isinstance(row[0], (str, int, float)):
            return str(row[0])

    # Caso 2: usa find_section per trovare righe 'pint' annidate/liste
    rows = find_section(param, ['pint']) if param is not None else None
    if rows:
        row0 = rows[0]
        if row0 and isinstance(row0[0], (str, int, float)):
            return str(row0[0])

    return None


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
        except Exception:
            operand = -999999
        try:
            address = int(di_fields[i + 1])
        except Exception:
            address = -999999
        try:
            operator = int(di_fields[i + 2])
        except Exception:
            operator = -999999
        groups.append((operand, address, operator))  # (OPERAND, ADDRESS, OPERATOR)
        i += DI_EXPR_GROUP_SIZE
    return groups


def run_di_search(data: Any, target_number: int) -> None:
    """Esegue l'intera ricerca DI (stampa come nel ramo # ---- Ricerche su DI ----)."""
    di_list = (data.get('io') or {}).get('di')  # lista indicizzata
    if not di_list:
        print("Sezione 'di' non trovata.")
        return

    # Campi EXPR nei -io.di
    matches = search_di_matches(di_list, target_number)
    if matches:
        for di_idx, exprtype_str, group_idx in matches:
            print(f"IO>DI>{di_idx} - {exprtype_str} - EXPRESSION N°{group_idx}")

    # Campo TIMEOUT dei CALC nei -io.di (IN)
    in_matches = search_di_in_matches(di_list, target_number)
    for di_idx in in_matches:
        print(f"IO>DI>{di_idx} - TIMEOUT match")

    # Campo IN dei -io.do
    do_list = (data.get('io') or {}).get('do')
    if do_list:
        do_matches = search_do_in_matches(do_list, target_number)
        for do_idx, name in do_matches:
            if name:
                print(f"IO>DO>{do_idx} - IN match (-do) - DO name: {name}")
            else:
                print(f"IO>DO>{do_idx} - IN match (-do)")

    # Campi FB_ERR_DEPRECATED/RESETIND nei -obj.fb
    fb_list = (data.get('obj') or {}).get('fb')
    if fb_list:
        fb_matches = search_fb_err_deprecated_matches(fb_list, target_number)
        for fb_idx, fb_type in fb_matches:
            print(f"FEEDBACK>{fb_idx} - FB_ERR_DEPRECATED match (-fb)")

        fb_reset_matches = search_fb_resetind_matches(fb_list, target_number)
        for fb_idx, fb_type in fb_reset_matches:
            print(f"FEEDBACK>{fb_idx} - RESETIND match (-fb)")

    # Campi DIG*/ENAB*/ACT nei -obj.input
    input_list = (data.get('obj') or {}).get('input')
    if input_list:
        in_input_matches = search_input_di_field_matches(input_list, target_number)
        for inp_idx, fields in in_input_matches:
            print(f"INPUT>{inp_idx} - match (-input) - fields: {', '.join(fields)}")

    # Campi ACT/ENAB* nei -obj.output
    output_list = (data.get('obj') or {}).get('output')
    if output_list:
        out_matches = search_output_di_field_matches(output_list, target_number)
        for out_idx, fields in out_matches:
            print(f"OUTPUT>{out_idx} - match (-output) - fields: {', '.join(fields)}")

    # Campi LS*/TR*/STAT/STARTING nei -obj.mot
    mot_list = (data.get('obj') or {}).get('mot')
    if mot_list:
        mot_matches = search_mot_di_field_matches(mot_list, target_number)
        for mot_idx, fields in mot_matches:
            print(f"MOT>{mot_idx} - match (-mot) - fields: {', '.join(fields)}")

    # Campi -obj.axis.int
    axis_int_lists = _find_axis_int_lists(data.get('obj'))
    if axis_int_lists:
        axis_matches = search_axis_int_di_field_matches(axis_int_lists, target_number)
        for axis_idx, fields in axis_matches:
            print(f"AXIS>{axis_idx} - match (-axis.int) - fields: {', '.join(fields)}")

    # Campi generici configurazione nei -in
    in_matches2 = search_in_field_matches(data, target_number)
    for pid, idx, label, origin in in_matches2:
        if label and origin:
            print(f"*IN>{pid}[{idx}] - match (-in) - label: {label} ({origin})")
        elif label:
            print(f"*IN>{pid}[{idx}] - match (-in) - label: {label}")
        else:
            print(f"*IN>{pid}[{idx}] - match (-in)")

    # Campi IN/ENAB/DISAB/REQACK/ACK nei -obj.alarm
    alarm_list = (data.get('obj') or {}).get('alarm')
    if alarm_list:
        alarm_matches = search_alarm_di_field_matches(alarm_list, target_number)
        for alarm_idx, fields, name in alarm_matches:
            if name:
                print(f"ALARMS/MAINT>ALARM>{alarm_idx} - match (-alarm) - fields: {', '.join(fields)} - name: {name}")
            else:
                print(f"ALARMS/MAINT>ALARM>{alarm_idx} - match (-alarm) - fields: {', '.join(fields)}")

    # Campo CAMPO_2/IN/RESET/ENABLED nei -ri se tipo = "IO_DI"
    ri_list = (data.get('io') or {}).get('ri')
    if ri_list:
        ri_matches = search_ri_di_field_matches(ri_list, target_number)
        for ri_idx, fields, name in ri_matches:
            if name:
                print(f"IO>RI>{ri_idx} - match (-ri) - fields: {', '.join(fields)} - name: {name}")
            else:
                print(f"IO>RI>{ri_idx} - match (-ri) - fields: {', '.join(fields)}")


def run_do_serach(data: Any, target_number: int) -> None:
    """Esegue la ricerca di un DO dato l'indice di -out."""
    # --- dove viene usato ---
    # Campi IN nei -io.do
    do_list = (data.get('io') or {}).get('do')
    if do_list:
        matches = search_do_in_matches(do_list, target_number)
        for do_idx, name in matches:
            if name:
                print(f"IO>DO>{do_idx} - IN match - DO name: {name}")
            else:
                print(f"IO>DO>{do_idx} - IN match")

    # 2) Campi DIG*/CC/DIG1ADD/DIG2ADD/ADVSTART/ADVENABLE/ADVBRAKE nei -obj.output
    output_list = (data.get('obj') or {}).get('output')
    if output_list:
        matches = search_output_do_field_matches(output_list, target_number)
        for out_idx, fields in matches:
            print(f"OUTPUT>{out_idx} - match (-output) - fields: {', '.join(fields)}")

    # 3) Campi CMD* dei -obj.mot
    mot_list = (data.get('obj') or {}).get('mot')
    if mot_list:
        matches = search_mot_do_field_matches(mot_list, target_number)
        for mot_idx, fields in matches:
            print(f"MOT>{mot_idx} - match (-mot) - fields: {', '.join(fields)}")

    # 4) Campo OUT dei obj.alarm
    alarm_list = (data.get('obj') or {}).get('alarm')
    if alarm_list:
        for alarm_idx, alarm_fields in enumerate(alarm_list):
            if not isinstance(alarm_fields, list) or len(alarm_fields) <= 5:
                continue
            try:
                out_val = int(alarm_fields[5])  # OUT
            except Exception:
                continue
            if out_val == target_number:
                name = alarm_fields[0] if alarm_fields and isinstance(alarm_fields[0], str) else None
                if name:
                    print(f"ALARMS/MAINT>ALARM>{alarm_idx} - OUT match - name: {name}")
                else:
                    print(f"ALARMS/MAINT>ALARM>{alarm_idx} - OUT match")

    # 5) Campi generici configurazione nei -out
    out_matches2 = search_out_field_matches(data, target_number)
    for pid, idx, label, origin in out_matches2:
        if label and origin:
            print(f"*OUT>{pid}[{idx}] - match (-out) - label: {label} ({origin})")
        elif label:
            print(f"*OUT>{pid}[{idx}] - match (-out) - label: {label}")
        else:
            print(f"*OUT>{pid}[{idx}] - match (-out)")

    # Campo IO_INT_ADDR2 nei -ri se tipo = "IO_DO"
    ri_list = (data.get('io') or {}).get('ri')
    if ri_list:
        ri_matches = search_ri_do_field_matches(ri_list, target_number)
        for ri_idx, fields, name in ri_matches:
            if name:
                print(f"IO>RI>{ri_idx} - match (-ri DO) - fields: {', '.join(fields)} - name: {name}")
            else:
                print(f"IO>RI>{ri_idx} - match (-ri DO) - fields: {', '.join(fields)}")


def run_ai_search(data: Any, target_number: int) -> None:
    # Campi IN dei -io.ao
    ao_list = (data.get('io') or {}).get('ao', [])
    if ao_list:
        matches = search_ai_in_ao_matches(ao_list, target_number, only_bus=True)
        if matches:
            for ao_idx, where, name in matches:
                if name:
                    print(f"IO>AO>{ao_idx} - {where} match - AO name: {name}")
                else:
                    print(f"IO>AO>{ao_idx} - {where} match")

    # Campi ININD dei -obj.fb (solo se tipo AI o AI2)
    fb_list = (data.get('obj') or {}).get('fb')
    if fb_list:
        inind_matches = search_fb_inind_ai_matches(fb_list, target_number)
        for fb_idx, fb_type in inind_matches:
            if fb_type:
                print(f"FEEDBACK>{fb_idx} - ININD match (-fb) - type: {fb_type}")
            else:
                print(f"FEEDBACK>{fb_idx} - ININD match (-fb)")

    # Campi ANA/SUP dei -obj.input
    input_list = (data.get('obj') or {}).get('input')
    if input_list:
        for inp_idx, fields in search_input_ai_field_matches(input_list, target_number):
            print(f"INPUT>{inp_idx} - match (-input) - fields: {', '.join(fields)}")

    # Campi STATUS*PSLCAN dei -obj.output
    output_list = (data.get('obj') or {}).get('output')
    if output_list:
        for out_idx, fields in search_output_ai_field_matches(output_list, target_number):
            print(f"OUTPUT>{out_idx} - match (-output) - fields: {', '.join(fields)}")

    # Campo RCSELAI nei -pint
    param = data.get('param')
    if param and search_param_pint_rcselai(param, target_number):
        print("PARAM>pint - RCSELAI match config>params>radiocontrol>in")

    # Campo IO_INT_ADDR2 nei -ri se tipo = "IO_AI"
    ri_list = (data.get('io') or {}).get('ri')
    if ri_list:
        ri_matches = search_ri_ai_field_matches(ri_list, target_number)
        for ri_idx, fields, name in ri_matches:
            if name:
                print(f"IO>RI>{ri_idx} - match (-ri AI) - fields: {', '.join(fields)} - name: {name}")
            else:
                print(f"IO>RI>{ri_idx} - match (-ri AI) - fields: {', '.join(fields)}")


def run_ao_search(data: Any, target_number: int) -> None:
    """Esegue la ricerca di un AO dato l'indice di -out."""

    # 1) Campi IN/AODUAL nei -io.ao
    ao_list = (data.get('io') or {}).get('ao', [])
    if ao_list:
        matches = search_ai_in_ao_matches(ao_list, target_number, only_bus=False)
        for ao_idx, where, name in matches:
            if name:
                print(f"IO>AO>{ao_idx} - {where} match (-ao) - AO name: {name}")
            else:
                print(f"IO>AO>{ao_idx} - {where} match (-ao)")

    # 2) Campi nei -obj.output (ANA1, ANA2, CTRL*PSLCAN)
    output_list = (data.get('obj') or {}).get('output')
    if output_list:
        for out_idx, fields in search_output_ao_field_matches(output_list, target_number):
            print(f"OUTPUT>{out_idx} - match (-output) - fields: {', '.join(fields)}")

    # 4) Campo IO_INT_ADDR2 nei -ri se tipo = "IO_AO"
    ri_list = (data.get('io') or {}).get('ri')
    if ri_list:
        ri_matches = search_ri_ao_field_matches(ri_list, target_number)
        for ri_idx, fields, name in ri_matches:
            if name:
                print(f"IO>RI>{ri_idx} - match (-ri AO) - fields: {', '.join(fields)} - name: {name}")
            else:
                print(f"IO>RI>{ri_idx} - match (-ri AO) - fields: {', '.join(fields)}")


def run_free_scan_di(data: Any) -> None:
    """Trova DI con nome vuoto o che contiene 'FREE' e, per ciascuno, esegue run_di_search sull'indice DI."""
    di_list = ((data.get('io') or {}).get('di')) or []
    if not di_list:
        print("Sezione 'di' non trovata.")
        return

    found: List[Tuple[int, str]] = []
    for di_idx, di_fields in enumerate(di_list):
        if not isinstance(di_fields, list) or not di_fields:
            continue
        raw_name = di_fields[0]
        name = (str(raw_name) if raw_name is not None else "").strip()
        if name == "" or ("FREE" in name.upper()):
            found.append((di_idx, name))

    if not found:
        print("Nessun DI con nome vuoto o contenente 'FREE' trovato.")
        return
    # INFO DEBUG
    # print(f"Trovati {len(found)} DI potenzialmente liberi:")
    # for di_idx, name in found:
        # shown = name if name != "" else '""'
        # print(f"  - DI[{di_idx}] nome={shown}")

    for di_idx, name in found:
        run_di_search(data, di_idx)


def run_free_scan_do(data: Any) -> None:
    do_list = ((data.get('io') or {}).get('do')) or []
    if not do_list:
        print("Sezione 'do' non trovata.")
        return

    found: List[Tuple[int, str]] = []
    for do_idx, do_fields in enumerate(do_list):
        if not isinstance(do_fields, list) or not do_fields:
            continue
        raw_name = do_fields[0]
        name = (str(raw_name) if raw_name is not None else "").strip()
        if name == "" or ("FREE" in name.upper()):
            found.append((do_idx, name))

    if not found:
        print("Nessun DO con nome vuoto o contenente 'FREE' trovato.")
        return

    for do_idx, _ in found:
        run_do_serach(data, do_idx)


def run_free_scan_ai(data: Any) -> None:
    ai_list = ((data.get('io') or {}).get('ai')) or []
    if not ai_list:
        print("Sezione 'ai' non trovata.")
        return

    found: List[Tuple[int, str]] = []
    for ai_idx, ai_fields in enumerate(ai_list):
        if not isinstance(ai_fields, list) or not ai_fields:
            continue
        raw_name = ai_fields[0]
        name = (str(raw_name) if raw_name is not None else "").strip()
        if name == "" or ("FREE" in name.upper()):
            found.append((ai_idx, name))

    if not found:
        print("Nessun AI con nome vuoto o contenente 'FREE' trovato.")
        return

    for ai_idx, _ in found:
        run_ai_search(data, ai_idx)


def run_free_scan_ao(data: Any) -> None:
    ao_list = ((data.get('io') or {}).get('ao')) or []
    if not ao_list:
        print("Sezione 'ao' non trovata.")
        return

    found: List[Tuple[int, str]] = []
    for ao_idx, ao_fields in enumerate(ao_list):
        if not isinstance(ao_fields, list) or not ao_fields:
            continue
        raw_name = ao_fields[0]
        name = (str(raw_name) if raw_name is not None else "").strip()
        if name == "" or ("FREE" in name.upper()):
            found.append((ao_idx, name))

    if not found:
        print("Nessun AO con nome vuoto o contenente 'FREE' trovato.")
        return

    for ao_idx, _ in found:
        run_ao_search(data, ao_idx)


def get_axis_int_di(data: Any, axis_index: int, label: str) -> Optional[int]:
    """Ritorna il DI configurato nell'array AXIS.INT per l'asse e la label dati."""
    axis_nodes = ((data.get('obj') or {}).get('axis') or [])
    try:
        node = axis_nodes[axis_index]
        arr = node.get('int')
        if not isinstance(arr, list):
            return None
        pos = IDX_AXIS_INT[label.strip().upper()]
        val = arr[pos]
        return int(val) if val is not None and str(val).strip() != '' else None
    except Exception:
        return None


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


def search_di_in_matches(di_list: List[list], target_number: int) -> List[int]:
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


def search_ai_in_ao_matches(ao_list: List[list], target_number: int, only_bus: bool = True) -> List[Tuple[int, str, Optional[str]]]:
    """
    Cerca tutti gli AO che referenziano l'AI `target_number` in IN o AODUAL.
    Se only_bus=True, considera solo AO con ADDRESS PNET(0) o CAN(1).
    Ritorna: [(indice_ao, 'IN'|'AODUAL', nome_ao_opzionale)]
    """
    matches: List[Tuple[int, str, Optional[str]]] = []
    for ao_index, ao_fields in enumerate(ao_list or []):
        if ao_index == 47:
            x = 1
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


def search_fb_inind_ai_matches(fb_list: List[list], target_number: int) -> List[Tuple[int, Optional[str]]]:
    """
    Cerca in -obj.fb le righe con FB_TYPE AI (1) o AI2 (7) che hanno ININD (idx 3)
    uguale a target_number.

    Ritorna: [(indice_fb, fb_type_string_opzionale)]
    """
    results: List[Tuple[int, Optional[str]]] = []
    AI_TYPES = {1, 7}  # 1=AI, 7=AI2

    for fb_index, fb_fields in enumerate(fb_list or []):
        if not isinstance(fb_fields, list):
            continue

        # Tipo FB
        fb_type_val = None
        if len(fb_fields) > IDX_FB_TYPE:
            try:
                fb_type_val = int(fb_fields[IDX_FB_TYPE])
            except Exception:
                fb_type_val = None

        if fb_type_val not in AI_TYPES:
            continue  # considera solo AI/AI2

        # ININD
        if len(fb_fields) <= IDX_FB_ININD:
            continue
        try:
            inind_val = int(fb_fields[IDX_FB_ININD])
        except Exception:
            continue

        if inind_val == target_number:
            fb_type_str = FB_TYPE.get(fb_type_val, str(fb_type_val) if fb_type_val is not None else None)
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


def search_output_do_field_matches(output_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca nei -obj.output i campi che referenziano un DO `target_number`.

    Campi verificati:
      - Sempre: DIG1 (idx 3), DIG2 (idx 4), CC (idx 5)
      - Se OUTPUT_TYPE = SELSLOW (3): ANA1 -> DIG1ADD, ANA2 -> DIG2ADD
      - Se OUTPUT_TYPE = ADV (4): ANA2 -> ADVSTART, DIG1 -> ADVENABLE, DIG2 -> ADVBRAKE

    Ritorna: [(indice_output, [nomi_campi_match])]
             dove i nomi sono simbolici (es. 'DIG1', 'DIG1ADD', 'ADVSTART', 'ADVENABLE', 'ADVBRAKE').
    """
    if not isinstance(output_list, list):
        return []

    # Indici di colonna nella riga -obj.output
    IDX_DIG1 = 3
    IDX_DIG2 = 4
    IDX_CC = 5

    results: List[Tuple[int, List[str]]] = []

    for out_index, out_fields in enumerate(output_list):
        if not isinstance(out_fields, list):
            continue

        matched: List[str] = []

        # Leggi OUTPUT_TYPE in modo robusto
        out_type = -1
        if len(out_fields) > IDX_OUTPUT_TYPE:
            try:
                out_type = int(out_fields[IDX_OUTPUT_TYPE])
            except Exception:
                out_type = -1

        # Helper per confronto robusto su un indice
        def _match_at(idx: int) -> bool:
            if idx < 0 or idx >= len(out_fields):
                return False
            try:
                val = int(out_fields[idx])
            except Exception:
                return False
            return val == target_number

        # Campi sempre presenti
        if _match_at(IDX_DIG1):
            matched.append("DIG1")
        if _match_at(IDX_DIG2):
            matched.append("DIG2")
        if _match_at(IDX_CC):
            matched.append("CC")

        # Rimappature per SELSLOW (OUTPUT_TYPE = 3): ANA1 -> DIG1ADD, ANA2 -> DIG2ADD
        if out_type == 3:
            if len(out_fields) > IDX_OUTPUT_ANA1 and _match_at(IDX_OUTPUT_ANA1):
                matched.append("DIG1ADD")
            if len(out_fields) > IDX_OUTPUT_ANA2 and _match_at(IDX_OUTPUT_ANA2):
                matched.append("DIG2ADD")

        # Rimappature per ADV:
        #   ANA2 -> ADVSTART
        #   DIG1 -> ADVENABLE (già controllato come DIG1; rinominiamo semanticamente)
        #   DIG2 -> ADVBRAKE  (già controllato come DIG2; rinominiamo semanticamente)
        if out_type == key_for_value(OUTPUT_TYPE, "ADV"):
            if len(out_fields) > IDX_OUTPUT_ANA2 and _match_at(IDX_OUTPUT_ANA2):
                matched.append("ADVSTART")
            # Se DIG1/2 hanno fatto match sopra, aggiungiamo anche i nomi semantici
            if "DIG1" in matched:
                matched.append("ADVENABLE")
            if "DIG2" in matched:
                matched.append("ADVBRAKE")

        if matched:
            results.append((out_index, matched))

    return results


def search_input_ai_field_matches(input_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in obj>input i campi ANA e SUP che referenziano l'AI `target_number`.
    Ritorna: [(indice_input, [nomi_campi_match])]
    """
    results: List[Tuple[int, List[str]]] = []
    for inp_idx, inp_fields in enumerate(input_list or []):
        if not isinstance(inp_fields, list):
            continue
        matched: List[str] = []
        if len(inp_fields) > IDX_INPUT_ANA:
            try:
                if int(inp_fields[IDX_INPUT_ANA]) == target_number:
                    matched.append("ANA")
            except Exception:
                pass
        if len(inp_fields) > IDX_INPUT_SUP:
            try:
                if int(inp_fields[IDX_INPUT_SUP]) == target_number:
                    matched.append("SUP")
            except Exception:
                pass
        if matched:
            results.append((inp_idx, matched))
    return results


def search_output_ai_field_matches(output_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in obj>output i campi STATUS*PSLCAN che referenziano l'AI `target_number`,
    ma solo se OUTPUT_TYPE è PSLCAN.
    """
    results: List[Tuple[int, List[str]]] = []

    for out_idx, out_fields in enumerate(output_list or []):
        if not isinstance(out_fields, list):
            continue

        matched: List[str] = []

        # leggi OUTPUT_TYPE
        out_type = -1
        if len(out_fields) > IDX_OUTPUT_TYPE:
            try:
                out_type = int(out_fields[IDX_OUTPUT_TYPE])
            except Exception:
                out_type = -1

        # STATUS*PSLCAN: solo se tipo == 6 (PSLCAN)
        if out_type == 6:
            for label, idx in [
                ("STATUS1PSLCAN", IDX_OUTPUT_STATUS1PSLCAN),
                ("STATUS2PSLCAN", IDX_OUTPUT_STATUS2PSLCAN),
            ]:
                if len(out_fields) > idx:
                    try:
                        if int(out_fields[idx]) == target_number:
                            matched.append(label)
                    except Exception:
                        pass

        if matched:
            results.append((out_idx, matched))

    return results


def search_output_ao_field_matches(output_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in obj>output i campi che referenziano AO.
    - Default: ANA1, ANA2
    - ADV (OUTPUT_TYPE = 5): nessun campo AO
    - PSLCAN (OUTPUT_TYPE = 6): CTRL1PSLCAN, CTRL2PSLCAN
    """
    results: List[Tuple[int, List[str]]] = []

    for out_idx, out_fields in enumerate(output_list or []):
        if not isinstance(out_fields, list):
            continue

        matched: List[str] = []

        # OUTPUT_TYPE
        out_type = -1
        if len(out_fields) > IDX_OUTPUT_TYPE:
            try:
                out_type = int(out_fields[IDX_OUTPUT_TYPE])
            except Exception:
                out_type = -1

        # --- Default: ANA1/ANA2 ---
        if out_type not in (5, 6):  # non ADV, non PSLCAN
            for label, idx in [("ANA1", IDX_OUTPUT_ANA1), ("ANA2", IDX_OUTPUT_ANA2)]:
                if len(out_fields) > idx:
                    try:
                        if int(out_fields[idx]) == target_number:
                            matched.append(label)
                    except Exception:
                        pass

        # --- ADV: nessun AO ---
        elif out_type == 5:
            pass

        # --- PSLCAN: CTRL1PSLCAN, CTRL2PSLCAN ---
        elif out_type == 6:
            for label, idx in [("CTRL1PSLCAN", IDX_OUTPUT_RPM), ("CTRL2PSLCAN", IDX_OUTPUT_CC)]:
                if len(out_fields) > idx:
                    try:
                        if int(out_fields[idx]) == target_number:
                            matched.append(label)
                    except Exception:
                        pass

        if matched:
            results.append((out_idx, matched))

    return results


def search_ri_ao_field_matches(ri_list: List[list], target_number: int) -> List[Tuple[int, List[str], Optional[str]]]:
    """
    Cerca nei -io.ri il campo IO_INT_ADDR2 che referenzia l'AO `target_number`,
    solo se ADDRESS = 3 (IO_AO).
    """
    results: List[Tuple[int, List[str], Optional[str]]] = []
    for ri_idx, ri_fields in enumerate(ri_list or []):
        if not isinstance(ri_fields, list):
            continue

        addr_val = None
        if len(ri_fields) > IDX_RI_ADDRESS:
            try:
                addr_val = int(ri_fields[IDX_RI_ADDRESS])
            except Exception:
                addr_val = None
        if addr_val != 3:  # solo IO_AO
            continue

        matched: List[str] = []
        if len(ri_fields) > IDX_RI_IO_INT_ADDR2:
            try:
                if int(ri_fields[IDX_RI_IO_INT_ADDR2]) == target_number:
                    matched.append("IO_INT_ADDR2")
            except Exception:
                pass

        if matched:
            name: Optional[str] = None
            if ri_fields and isinstance(ri_fields[0], str):
                name = ri_fields[0]
            results.append((ri_idx, matched, name))
    return results


def search_param_pint_rcselai(param_node: Any, target_number: int) -> bool:
    """
    Cerca in param>pint il campo RCSELAI uguale a target_number.
    Restituisce True se trovato, altrimenti False.
    """
    rows = find_section(param_node, ['pint'])
    if not rows:
        return False

    # secondo la tua struttura RCSELAI è al penultimo indice di pint
    for row in rows:
        if not isinstance(row, list):
            continue
        try:
            if int(row[IDX_RCSELAI]) == target_number:
                return True
        except Exception:
            continue
    return False


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


def search_mot_do_field_matches(mot_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca nei -obj.mot i campi che referenziano un DO `target_number`.

    Campi verificati (indici nella riga mot):
      - CMD  (idx 8)
      - CMD1 (idx 11)
      - CMD2 (idx 12)
      - CMD3 (idx 13)

    Ritorna: [(indice_mot, [nomi_campi_match])]
    """
    if not isinstance(mot_list, list):
        return []

    # Indici costanti per i campi DO nei -obj.mot
    IDX_CMD = 8
    IDX_CMD1 = 11
    IDX_CMD2 = 12
    IDX_CMD3 = 13

    results: List[Tuple[int, List[str]]] = []

    for mot_idx, mot_fields in enumerate(mot_list or []):
        if not isinstance(mot_fields, list):
            continue

        matched: List[str] = []

        def _match_at(idx: int) -> bool:
            if idx < 0 or idx >= len(mot_fields):
                return False
            try:
                val = int(mot_fields[idx])
            except Exception:
                return False
            return val == target_number

        if _match_at(IDX_CMD):
            matched.append("CMD")
        if _match_at(IDX_CMD1):
            matched.append("CMD1")
        if _match_at(IDX_CMD2):
            matched.append("CMD2")
        if _match_at(IDX_CMD3):
            matched.append("CMD3")

        if matched:
            results.append((mot_idx, matched))

    return results


def search_alarm_di_field_matches(alarm_list: List[list], target_number: int) -> List[Tuple[int, List[str], Optional[str]]]:
    """
    Cerca nei -obj.alarm i campi IN, ENAB, DISAB, REQACK, ACK che referenziano il DI `target_number`.
    Ritorna: [(indice_alarm, [nomi_campi_match], nome_alarm opz.)]
    """
    results: List[Tuple[int, List[str], Optional[str]]] = []
    fields = [
        ("IN", IDX_ALARM_IN),
        ("ENAB", IDX_ALARM_ENAB),
        ("DISAB", IDX_ALARM_DISAB),
        ("REQACK", IDX_ALARM_REQACK),
        ("ACK", IDX_ALARM_ACK),
    ]
    for alarm_idx, alarm_fields in enumerate(alarm_list or []):
        if not isinstance(alarm_fields, list):
            continue
        matched: List[str] = []
        for label, idx in fields:
            if len(alarm_fields) > idx:
                try:
                    val = int(alarm_fields[idx])
                except Exception:
                    continue
                if val == target_number:
                    matched.append(label)
        if matched:
            name: Optional[str] = None
            if len(alarm_fields) > 0 and isinstance(alarm_fields[0], (str, int, float)):
                name = str(alarm_fields[0])
            results.append((alarm_idx, matched, name))
    return results


def search_axis_int_di_field_matches(axis_int_lists: List[List[Any]], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in ciascun array 'axis.int' i campi etichettati (SUP, INF, ALTFBDIG, HH, H, L, LL,
    SAFETYUP1..6, H0, L0, INDMEM, SAFETYDOWN1..6, DECOUPLE1AUTO..6, FREE70, FREE71,
    BPDISABLE1..12, OPTPARAM1..3) che referenziano il DI 'target_number'.
    Ritorna: [(indice_axis, [nomi_campi_match])]
    """
    results: List[Tuple[int, List[str]]] = []
    for axis_idx, arr in enumerate(axis_int_lists or []):
        if not isinstance(arr, list):
            continue
        matched: List[str] = []
        for label, idx in IDX_AXIS_INT.items():
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


def search_ri_di_field_matches(ri_list: List[list], target_number: int) -> List[Tuple[int, List[str], Optional[str]]]:
    """
    Cerca nei -io.ri i campi CAMPO_2, ENABLED, RESET e IN che referenziano il DI `target_number`.
    IN viene considerato solo se ADDRESS = 0 (IO_DI).
    Il match viene aggiunto ai risultati solo se IO_CAMPO_1 = 0 e ADDRESS > 3.
    Ritorna: [(indice_ri, [nomi_campi_match], nome_ri_opzionale)]
    """
    results: List[Tuple[int, List[str], Optional[str]]] = []

    for ri_idx, ri_fields in enumerate(ri_list or []):
        if not isinstance(ri_fields, list):
            continue

        matched: List[str] = []

        # --- CAMPO_2, ENABLED, RESET, ADDRESS ---
        for label, idx in [
            ("CAMPO_2", IDX_RI_CAMPO2),
            ("ENABLED", IDX_RI_ENABLED),
            ("RESET", IDX_RI_RESET),
        ]:
            if len(ri_fields) > idx:
                try:
                    if int(ri_fields[idx]) == target_number:
                        if label == "ADDRESS":
                            # prendi IO_CAMPO_1 per vedere se è DI (Const_IO.IO_DI)
                            if len(ri_fields) > IDX_RI_CAMPO1:
                                try:
                                    campo1_val = int(ri_fields[IDX_RI_CAMPO1])
                                except Exception:
                                    campo1_val = None
                                if campo1_val == Const_IO.IO_DI:
                                    matched.append(label)
                        else:
                            matched.append(label)
                except Exception:
                    pass

        # --- IN: solo se ADDRESS = 0 ---
        addr_val = None
        if len(ri_fields) > IDX_RI_ADDRESS:
            try:
                addr_val = int(ri_fields[IDX_RI_ADDRESS])
            except Exception:
                addr_val = None

        if addr_val == 0 and len(ri_fields) > IDX_RI_IN:
            try:
                if int(ri_fields[IDX_RI_IN]) == target_number:
                    matched.append("IN")
            except Exception:
                pass

        # ✅ --- FILTRO aggiuntivo: IO_CAMPO_1 = 0 e ADDRESS > 3 ---
        campo1_val = None
        if len(ri_fields) > IDX_RI_CAMPO1:
            try:
                campo1_val = int(ri_fields[IDX_RI_CAMPO1])
            except Exception:
                campo1_val = None

        if len(ri_fields) > IDX_RI_ADDRESS:
            try:
                addr_val_check = int(ri_fields[IDX_RI_ADDRESS])
            except Exception:
                addr_val_check = None
        else:
            addr_val_check = None

        # se IO_CAMPO_1 != 0 o ADDRESS <= 3 → scarta i match
        if matched and (campo1_val == IO_CAMPO_1 and addr_val_check is not None and addr_val_check > 3):
            name: Optional[str] = None
            if ri_fields and isinstance(ri_fields[0], str):
                name = ri_fields[0]
            results.append((ri_idx, matched, name))
        # else: se non soddisfa la condizione, non aggiunge niente

    return results


def search_ri_ai_field_matches(ri_list: List[list], target_number: int) -> List[Tuple[int, List[str], Optional[str]]]:
    """
    Cerca nei -io.ri il campo IO_INT_ADDR2 che referenzia l'AI `target_number`,
    solo se ADDRESS = 2 (IO_AI).
    Ritorna: [(indice_ri, [nomi_campi_match], nome_ri_opzionale)]
    """
    results: List[Tuple[int, List[str], Optional[str]]] = []

    for ri_idx, ri_fields in enumerate(ri_list or []):
        if not isinstance(ri_fields, list):
            continue

        # check ADDRESS
        addr_val = None
        if len(ri_fields) > IDX_RI_ADDRESS:
            try:
                addr_val = int(ri_fields[IDX_RI_ADDRESS])
            except Exception:
                addr_val = None

        if addr_val != 2:  # solo IO_AI
            continue

        matched: List[str] = []
        if len(ri_fields) > IDX_RI_IO_INT_ADDR2:
            try:
                if int(ri_fields[IDX_RI_IO_INT_ADDR2]) == target_number:
                    matched.append("IO_INT_ADDR2")
            except Exception:
                pass

        if matched:
            name: Optional[str] = None
            if ri_fields and isinstance(ri_fields[0], str):
                name = ri_fields[0]
            results.append((ri_idx, matched, name))

    return results


def search_ri_do_field_matches(ri_list: List[list], target_number: int) -> List[Tuple[int, List[str], Optional[str]]]:
    """
    Cerca nei -io.ri il campo IO_INT_ADDR2 che referenzia il DO `target_number`,
    solo se ADDRESS = 1 (IO_DO).
    Ritorna: [(indice_ri, [nomi_campi_match], nome_ri_opzionale)]
    """
    results: List[Tuple[int, List[str], Optional[str]]] = []

    for ri_idx, ri_fields in enumerate(ri_list or []):
        if not isinstance(ri_fields, list):
            continue

        # check ADDRESS
        addr_val = None
        if len(ri_fields) > IDX_RI_ADDRESS:
            try:
                addr_val = int(ri_fields[IDX_RI_ADDRESS])
            except Exception:
                addr_val = None

        if addr_val != 1:  # solo IO_DO
            continue

        matched: List[str] = []
        if len(ri_fields) > IDX_RI_IO_INT_ADDR2:
            try:
                if int(ri_fields[IDX_RI_IO_INT_ADDR2]) == target_number:
                    matched.append("IO_INT_ADDR2")
            except Exception:
                pass

        if matched:
            name: Optional[str] = None
            if ri_fields and isinstance(ri_fields[0], str):
                name = ri_fields[0]
            results.append((ri_idx, matched, name))

    return results
# ---- Ricerca nei campi -in ---------------------------------------------------


def _find_in_arrays(root: Any) -> List[List[Any]]:
    """Raccoglie tutte le liste associate alla chiave 'in' in obj."""
    return find_section(root, ['in']) or []


def _is_mostly_ints(arr: List[Any]) -> bool:
    ints = 0
    for v in arr:
        try:
            if isinstance(v, bool):
                continue
            int(v)  # prova cast
            ints += 1
        except Exception:
            pass
    return ints >= max(1, len(arr) // 2)


def _is_mostly_strings(arr: List[Any]) -> bool:
    strings = sum(1 for v in arr if isinstance(v, str))
    return strings >= max(1, len(arr) // 2)


# ---- Ricerca nei campi -out --------------------------------------------------


def _find_out_arrays(root: Any) -> List[List[Any]]:
    """Raccoglie tutte le liste associate alla chiave 'out' in obj."""
    return find_section(root, ['out']) or []


def _pair_out_arrays(out_arrays: List[List[Any]]) -> List[Tuple[int, Optional[List[Any]], Optional[List[Any]]]]:
    """
    Abbina array numerici a array di etichette come in _pair_in_arrays,
    minimizzando la differenza di lunghezza e preferendo la labels-list più lunga a parità.
    """
    numeric = [(i, a) for i, a in enumerate(out_arrays) if _is_mostly_ints(a)]
    labels = [(i, a) for i, a in enumerate(out_arrays) if _is_mostly_strings(a)]

    pairs: List[Tuple[int, Optional[List[Any]], Optional[List[Any]]]] = []
    used = set()
    pid = 0

    for _, n in numeric:
        best_j = None
        best_la = None
        best_key = None  # (diff, -len)
        for j, (li, la) in enumerate(labels):
            if j in used:
                continue
            diff = abs(len(la) - len(n))
            key = (diff, -len(la))
            if best_key is None or key < best_key:
                best_key = key
                best_j = j
                best_la = la
        if best_la is not None:
            used.add(best_j)
            pairs.append((pid, n, best_la))
        else:
            pairs.append((pid, n, None))
        pid += 1

    for j, (li, la) in enumerate(labels):
        if j not in used:
            pairs.append((pid, None, la))
            pid += 1

    return pairs


def search_out_field_matches(obj_node: Any, target_number: int) -> List[Tuple[int, int, Optional[str], Optional[str]]]:
    """
    Cerca il numero 'target_number' all'interno degli array '- out:' dovunque nel documento.
    Preferisce l'etichetta dalla lista labels abbinata; se mancante/insufficiente/'x',
    usa la mappatura per indice (OUT_INDEX_LABELS) per ricavare label e l'origine (config>...).

    Ritorna: [(pair_id, index, label_opzionale, origine_opzionale)]
    """
    results: List[Tuple[int, int, Optional[str], Optional[str]]] = []
    out_arrays = _find_out_arrays(obj_node)
    if not out_arrays:
        return results

    pairs = _pair_out_arrays(out_arrays)

    for pid, num_arr, lab_arr in pairs:
        if not num_arr:
            continue
        for idx, v in enumerate(num_arr):
            # confronto numerico robusto
            try:
                val = int(str(v).strip())
            except Exception:
                continue
            if val != target_number:
                continue

            # 1) prova a prendere la label dalla lista di etichette abbinata
            raw_label = lab_arr[idx] if (lab_arr and idx < len(lab_arr)) else None
            label = None
            if isinstance(raw_label, str):
                s = raw_label.strip()
                if s and s.lower() != 'x':
                    label = s

            # 2) se mancante/non utile, fallback alla mappa per indice
            if not label:
                label = _label_from_out_index(idx)

            # 3) calcola l'origine
            if label:
                origin = _infer_out_origin(label)
            else:
                # fallback: prova a dedurre l'origine dalla label mappata da indice
                mapped = _label_from_out_index(idx)
                origin = _infer_out_origin(mapped) if mapped else None

            results.append((pid, idx, label, origin))

    return results


def _label_from_in_index(idx: int) -> Optional[str]:
    if 0 <= idx < len(IN_INDEX_LABELS):
        lab = IN_INDEX_LABELS[idx]
        if isinstance(lab, str) and lab.strip().lower() != 'x' and lab.strip() != '':
            return lab.strip()
    return None


def _origin_from_in_index(idx: int) -> Optional[str]:
    lab = _label_from_in_index(idx)
    return _infer_in_origin(lab) if lab else None


def _label_from_out_index(idx: int) -> Optional[str]:
    if 0 <= idx < len(OUT_INDEX_LABELS):
        lab = OUT_INDEX_LABELS[idx]
        if isinstance(lab, str) and lab.strip().lower() != 'x' and lab.strip():
            return lab
    return None


def _infer_out_origin(label: str) -> Optional[str]:
    if not label:
        return None
    L = re.sub(r'[^A-Z0-9]', '', label.upper())
    for origin, names in OUT_ORIGIN_SETS.items():
        for n in names:
            if re.sub(r'[^A-Z0-9]', '', n.upper()) == L:
                return origin
    return None


def _normalize_label(s: str) -> str:
    # Uppercase e rimuove tutto ciò che non è A-Z/0-9 per confronti robusti
    return re.sub(r'[^A-Z0-9]', '', str(s).strip().upper())


def _infer_in_origin(label: str) -> Optional[str]:
    if not isinstance(label, str) or not label.strip():
        return None
    L = _normalize_label(label)

    # matching contro l'elenco noto, ma normalizzato
    for origin, names in IN_ORIGIN_SETS.items():
        for n in names:
            if _normalize_label(n) == L:
                return origin
    return None


def _pair_in_arrays(in_arrays: List[List[Any]]) -> List[Tuple[int, Optional[List[Any]], Optional[List[Any]]]]:
    numeric = [(i, a) for i, a in enumerate(in_arrays) if _is_mostly_ints(a)]
    labels = [(i, a) for i, a in enumerate(in_arrays) if _is_mostly_strings(a)]

    pairs: List[Tuple[int, Optional[List[Any]], Optional[List[Any]]]] = []
    used = set()
    pid = 0

    for _, n in numeric:
        # scegli la labels-list con differenza di lunghezza minima (preferendo quella più lunga a parità)
        best_j = None
        best_la = None
        best_key = None  # (diff, -len)
        for j, (li, la) in enumerate(labels):
            if j in used:
                continue
            diff = abs(len(la) - len(n))
            key = (diff, -len(la))
            if best_key is None or key < best_key:
                best_key = key
                best_j = j
                best_la = la
        if best_la is not None:
            used.add(best_j)
            pairs.append((pid, n, best_la))
        else:
            pairs.append((pid, n, None))
        pid += 1

    for j, (li, la) in enumerate(labels):
        if j not in used:
            pairs.append((pid, None, la))
            pid += 1

    return pairs


def search_in_field_matches(obj_node: Any, target_number: int) -> List[Tuple[int, int, Optional[str], Optional[str]]]:
    """
    Cerca il numero 'target_number' all'interno degli array '- in:' dovunque nel documento.
    Preferisce l'etichetta dalla lista labels abbinata; se mancante/insufficiente/'x',
    usa la mappatura per indice (IN_INDEX_LABELS) per ricavare label e origine.
    Ritorna: (pair_id, index, label_opzionale, origine_opzionale)
    """
    results: List[Tuple[int, int, Optional[str], Optional[str]]] = []
    in_arrays = _find_in_arrays(obj_node)
    if not in_arrays:
        return results

    pairs = _pair_in_arrays(in_arrays)

    for pid, num_arr, lab_arr in pairs:
        if not num_arr:
            continue
        for idx, v in enumerate(num_arr):
            # confronto numerico robusto
            try:
                val = int(str(v).strip())
            except Exception:
                continue
            if val != target_number:
                continue

            # 1) prova a prendere la label dalla lista di etichette abbinata
            raw_label = lab_arr[idx] if (lab_arr and idx < len(lab_arr)) else None
            label = None
            if isinstance(raw_label, str):
                s = raw_label.strip()
                if s and s.lower() != 'x':
                    label = s

            # 2) se mancante/non utile, fallback alla mappa per indice
            if not label:
                label = _label_from_in_index(idx)

            # 3) calcola l'origine
            origin = _infer_in_origin(label) if label else _origin_from_in_index(idx)

            results.append((pid, idx, label, origin))

    return results


def _pause_if_frozen():
    if getattr(sys, "frozen", False):  # eseguibile PyInstaller
        try:
            input("\nPremi Invio per chiudere...")
        except EOFError:
            pass


def main():
    # 1) Carico una volta il config
    cfg_path = choose_and_prepare_config()

    try:
        data = load_yaml(str(cfg_path))
    except Exception as e:
        print(f"Errore nel parsing YAML: {e}")
        _pause_if_frozen()
        return

    sn = get_sn_from_param(data)
    if sn:
        print(f"Caricato config della commessa: {sn}")

    # 2) Loop interattivo: ripeti la domanda dopo ogni ricerca
    while True:
        print("\n" + "-" * 60)
        tipo_opt = (0, 1, 2, 3, 4, 5, 7)
        tipo_raw = input("Che tipo stai cercando? (1=DI, 2=AI, 3=DO, 4=AO, 5=SYSTEM, 7=FREE, 0=REFRESH, Invio per uscire): ").strip().lower()
        if tipo_raw in ("", "q", "quit", "exit", "esci"):
            print("Uscita.")
            _pause_if_frozen()
            return

        try:
            tipo = int(tipo_raw)
        except ValueError:
            print("Tipo non valido. Inserisci 1, 2, 3, 4, 5 o 7.")
            continue

        if tipo not in tipo_opt:
            print("Tipo non valido. Usa 1=DI, 2=AI, 3=DO, 4=AO, 5=SYSTEM, 7=FREE.")
            continue

        print("-" * 60)

        # ====================== SYSTEM (nessuna richiesta numero qui) ======================

        if tipo == "0":
            fetch_again()
            
        if tipo == 5:
            # --- SYSTEM lookup: scegli TYPE -> INDEX -> FIELD, calcola numero e cerca nei DI ---
            print("Scegli il TYPE di sistema (nome o numero):")
            entries = [f"{val} = {name}" for name, val in sorted(SYSTEM_TYPE.items(), key=lambda kv: kv[1])]
            print_in_columns(entries, cols=4)
            sel = input("TYPE: ").strip()

            # Normalizzo la scelta (accetta sia numero sia nome)
            if sel.isdigit():
                type_id = int(sel)
                sys_type = SYSTEM_TYPE_REV.get(type_id)
                if not sys_type:
                    print("TYPE non valido.")
                    continue
            else:
                sys_type = sel.strip().upper()
                if sys_type not in SYSTEM_TYPE:
                    print("TYPE non valido.")
                    continue

            if sys_type not in ("AXIS", "ALARM"):
                print(f"TYPE '{sys_type}' non ancora supportato qui (solo AXIS/ALARM).")
                continue

            # --- Prima di chiedere l'indice, mostra mappa indice -> nome ---
            if sys_type == "AXIS":
                axis_nodes = ((data.get('obj') or {}).get('axis') or [])

                def axis_name(i: int) -> str:
                    try:
                        node = axis_nodes[i]
                        if isinstance(node, dict):
                            a = node.get('axis')
                            if isinstance(a, list) and a and isinstance(a[0], (str, int, float)):
                                return str(a[0])
                    except Exception:
                        pass
                    return f"axis[{i}]"

                n_to_show = min(len(axis_nodes), AXIS_MAX_INDEX + 1)

                print("\nMappa AXIS (indice → nome):")
                # prepara le stringhe "[ii] nome"
                entries = [f"[{i:02d}] {axis_name(i)}" for i in range(n_to_show)]
                if entries:
                    cols = 6  # raggruppa per 6
                    colw = max(len(s) for s in entries) + 2  # padding
                    for k in range(0, len(entries), cols):
                        row = entries[k:k + cols]
                        print("  " + "".join(s.ljust(colw) for s in row))

                if n_to_show < AXIS_MAX_INDEX + 1:
                    print(f"... (definiti {n_to_show} assi su {AXIS_MAX_INDEX + 1})")

                idx_prompt_max = AXIS_MAX_INDEX
            else:  # ALARM
                alarm_rows = ((data.get('obj') or {}).get('alarm') or [])
                print("\nAlcuni ALARM definiti (indice → nome):")
                for i, row in enumerate(alarm_rows):
                    try:
                        nm = row[0] if (
                                    isinstance(row, list) and row and isinstance(row[0], (str, int, float))) else None
                        if nm not in (None, "", "x", "X"):
                            print(f"  [{i:03d}] {nm}")
                    except Exception:
                        continue
                if len(alarm_rows) < ALARM_MAX_INDEX + 1:
                    print(f"(presenti {len(alarm_rows)} righe alarm; range massimo supportato 0..{ALARM_MAX_INDEX})")

                idx_prompt_max = ALARM_MAX_INDEX

            # --- Scelta INDEX con validazione ---
            try:
                idx_raw = input(f"\nInserisci INDEX per {sys_type} (0..{idx_prompt_max}): ").strip()
                index = int(idx_raw)
                validate_system_index(sys_type, index)
            except Exception as e:
                print(f"INDEX non valido: {e}")
                continue
            # --- Scelta modalità: System Address o DI da AXIS.INT ---
            if sys_type == "AXIS":
                # mode = (input("Vuoi cercare (1) indirizzo SYSTEM AXIS.* oppure (2) DI da AXIS.INT? [1/2]: ").strip() or "1") # per ora non (2)
                mode = 1
                if mode == "2":
                    # elenco dei campi disponibili in AXIS.INT
                    axis_int_fields = list(IDX_AXIS_INT.keys())
                    print("\nScegli FIELD di AXIS.INT (nome o indice):")
                    entries = [f"[{i:02d}] {lab}" for i, lab in enumerate(axis_int_fields)]
                    print_in_columns(entries, cols=3)
                    fsel2 = input("FIELD AXIS.INT: ").strip()

                    if fsel2.isdigit():
                        fidx2 = int(fsel2)
                        if not (0 <= fidx2 < len(axis_int_fields)):
                            print("FIELD AXIS.INT index fuori range.")
                            continue
                        field_int = axis_int_fields[fidx2]
                    else:
                        field_int = fsel2.strip().upper()
                        if field_int not in IDX_AXIS_INT:
                            print("FIELD AXIS.INT sconosciuto.")
                            continue

                    di_id = get_axis_int_di(data, index, field_int)
                    if di_id is None or di_id < 0:
                        print(f"AXIS.INT → {field_int}[{index}] non configurato (o valore invalido).")
                        continue

                    print(f"\nAXIS.INT → {field_int}[{index}]  => DI: {di_id}\n")
                    # usa la stessa identica ricerca DI
                    run_di_search(data, di_id)
                    # torna al menu principale
                    continue
            # --- Scelta FIELD (nome o indice) ---
            fields = AXIS_GROUPS_ORDER if sys_type == "AXIS" else ALARM_GROUPS_ORDER

            print(f"\nScegli FIELD per {sys_type} (nome o indice):")
            entries = [f"[{i:02d}] {name}" for i, name in enumerate(fields)]
            print_in_columns(entries, cols=3)

            fsel = input("FIELD: ").strip()

            if fsel.isdigit():
                fidx = int(fsel)
                if not (0 <= fidx < len(fields)):
                    print("FIELD index fuori range.")
                    continue
                field = fields[fidx]
            else:
                field = fsel.strip().upper()
                if field not in fields:
                    print("FIELD sconosciuto.")
                    continue

            # --- Calcolo del numero di sistema ---
            try:
                if sys_type == "AXIS":
                    number = make_axis_sys_addr(field, index)
                else:  # ALARM
                    number = make_alarm_sys_addr(field, index)
            except Exception as e:
                print(f"Errore nel calcolo dell'indirizzo di sistema: {e}")
                continue

            human = decode_system_addr(number) or f"{sys_type}.{field}[{index}]"
            print(f"\nSYSTEM → {human}  => numero: {number}")
            run_di_search(data, number)
            continue
        # ==================== /SYSTEM ====================

        # ====================== FREE (scan automatico) ======================
        if tipo == 7:
            print("DI:")
            run_free_scan_di(data)
            print("DO:")
            run_free_scan_do(data)
            print("AI")
            run_free_scan_ai(data)
            print("AO")
            run_free_scan_ao(data)
            continue
        # ==================== /FREE ======================

        # Per DI/AI/DO/AO (1..4) chiedo il numero da cercare
        if tipo in (1, 2, 3, 4):
            while True:
                target_str = input("Inserisci il numero da cercare (Invio per tornare al menu): ").strip()
                if target_str == "":
                    # esco dalla categoria e torno al menu principale (scelta tipo)
                    break
                try:
                    target_number = int(target_str)
                except ValueError:
                    print("Numero non valido. Riprova (Invio per tornare al menu).")
                    continue

                print("-" * 60)
                if tipo == 1:
                    run_di_search(data, target_number)
                elif tipo == 2:
                    run_ai_search(data, target_number)
                elif tipo == 3:
                    run_do_serach(data, target_number)
                elif tipo == 4:
                    run_ao_search(data, target_number)
            # finito il sottoloop, riparte il while principale
            continue


def print_in_columns(entries: List[str], cols: int = 3) -> None:
    if not entries:
        return
    colw = max(len(s) for s in entries) + 2  # padding
    for i in range(0, len(entries), cols):
        row = entries[i:i + cols]
        print("  " + "".join(s.ljust(colw) for s in row))


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if code not in (0, None):
            print(f"\n[EXIT] Codice: {code}")
        _pause_if_frozen()
        sys.exit(code)
    except Exception as e:
        print("\n[Errore inatteso]:", e)
        _pause_if_frozen()
        sys.exit(1)


# TODO: se non riesco a scaricare il file non devo chiudere il programma

# TODO: ricerca  
# TODO: