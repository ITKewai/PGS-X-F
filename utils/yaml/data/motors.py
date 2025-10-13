from utils.yaml.data.costants import *
from typing import Any, Dict, List, Optional, Tuple


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
