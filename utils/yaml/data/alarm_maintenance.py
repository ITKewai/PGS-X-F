from typing import Any, List, Tuple, Optional, Dict
from utils.yaml.data.costants import *


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
