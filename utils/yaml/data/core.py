from utils.exports.tia_constants import MAX_MAINT, MAX_ALARM, MAX_TOOLSET, MAX_MOTORE, MAX_ASSE
from utils.yaml.data.costants import *
from typing import Any, Dict, List, Optional, Tuple


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
    if not (0 <= axis_index <= MAX_ASSE):
        raise ValueError(f"axis_index fuori range (0..{MAX_ASSE}): {axis_index}")
    return AXIS_GROUP_BASE[g] + axis_index


def parse_axis_sys_addr(addr: int) -> Optional[Tuple[str, int]]:
    if addr < 2048 or addr >= 2048 + AXIS_GROUP_STEP * len(AXIS_GROUPS_ORDER):
        return None
    group_idx = (addr - 2048) // AXIS_GROUP_STEP
    if not (0 <= group_idx < len(AXIS_GROUPS_ORDER)):
        return None
    base = 2048 + group_idx * AXIS_GROUP_STEP
    axis_index = addr - base
    if not (0 <= axis_index <= MAX_ASSE):
        return None
    return AXIS_GROUPS_ORDER[group_idx], axis_index


def make_alarm_sys_addr(group: str, alarm_index: int) -> int:
    g = group.strip().upper()
    if g not in ALARM_GROUP_BASE:
        raise KeyError(f"Gruppo ALARM sconosciuto: {group}")
    if not (0 <= alarm_index <= MAX_ALARM):  # 0..191
        raise ValueError(f"alarm_index fuori range (0..{MAX_ALARM}): {alarm_index}")
    return ALARM_GROUP_BASE[g] + alarm_index


def parse_alarm_sys_addr(addr: int) -> Optional[Tuple[str, int]]:
    if addr < 16384 or addr >= 16384 + ALARM_GROUP_STEP * len(ALARM_GROUPS_ORDER):
        return None
    group_idx = (addr - 16384) // ALARM_GROUP_STEP
    if not (0 <= group_idx < len(ALARM_GROUPS_ORDER)):
        return None
    base = 16384 + group_idx * ALARM_GROUP_STEP
    alarm_index = addr - base
    if not (0 <= alarm_index <= MAX_ALARM):
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
        if not (0 <= index <= MAX_ASSE):
            raise ValueError(f"{t} index fuori range (0..{MAX_ASSE}): {index}")
    elif t == "MOTOR":
        if not (1 <= index <= MAX_MOTORE):
            raise ValueError(f"MOTOR index fuori range ({1}..{MAX_MOTORE}): {index}")
    elif t == "TOOLSET":
        if not (0 <= index <= MAX_TOOLSET):
            raise ValueError(f"TOOLSET index fuori range (0..{MAX_TOOLSET}): {index}")
    elif t == "ALARM":
        if not (0 <= index <= MAX_ALARM):
            raise ValueError(f"ALARM index fuori range (0..{MAX_ALARM}): {index}")
    elif t == "MAINT":
        if not (0 <= index <= MAX_MAINT):
            raise ValueError(f"MAINT index fuori range (0..{MAX_MAINT}): {index}")
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


def find_axis_int_lists(root: Any) -> List[List[Any]]:
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
