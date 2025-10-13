from utils.yaml.data.core import *
from utils.yaml.data.costants import *
from typing import Any, Dict, List, Optional, Tuple


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

# ---- Ricerca nei campi -in ---------------------------------------------------


def find_in_arrays(root: Any) -> List[List[Any]]:
    """Raccoglie tutte le liste associate alla chiave 'in' in obj."""
    return find_section(root, ['in']) or []


def is_mostly_ints(arr: List[Any]) -> bool:
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


def is_mostly_strings(arr: List[Any]) -> bool:
    strings = sum(1 for v in arr if isinstance(v, str))
    return strings >= max(1, len(arr) // 2)
