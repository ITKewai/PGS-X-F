from utils.yaml.data.costants import *
from typing import Any, Dict, List, Optional, Tuple


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
