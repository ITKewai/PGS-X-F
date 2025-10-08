
from typing import Any, List, Tuple, Optional, Dict
from utils.yaml.data.costants import *


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
