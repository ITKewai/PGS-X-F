from typing import Any, List, Tuple, Optional, Dict
from utils.yaml.data.costants import *
from utils.yaml.data.core import *
from utils.yaml.data.humanize import *
from utils.yaml.data.input import *


def search_output_ai_field_matches(output_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in obj>output i campi STATUS*PSLCAN che referenziano l'AI `target_number`,
    ma solo se OUTPUT_TYPE è PSLCAN.
    """
    results: List[Tuple[int, List[str]]] = []

    for out_idx, out_fields in enumerate(output_list or []):
        # print(out_idx, out_fields)
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
                ("STATUS1PSLCAN", IDX_INPUT_STATUS1PSLCAN),
                ("STATUS2PSLCAN", IDX_INPUT_STATUS2PSLCAN),
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
            for label, idx in [("CTRL1PSLCAN", IDX_OUTPUT_STATUS1PSLCAN), ("CTRL2PSLCAN", IDX_OUTPUT_STATUS2PSLCAN)]:
                if len(out_fields) > idx:
                    try:
                        if int(out_fields[idx]) == target_number:
                            print(out_fields)
                            matched.append(label)
                    except Exception:
                        pass

        if matched:
            results.append((out_idx, matched))

    return results

# ---- Ricerca nei campi -out --------------------------------------------------

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
                label = label_from_out_index(idx)

            # 3) calcola l'origine
            if label:
                origin = infer_out_origin(label)
            else:
                # fallback: prova a dedurre l'origine dalla label mappata da indice
                mapped = label_from_out_index(idx)
                origin = infer_out_origin(mapped) if mapped else None

            results.append((pid, idx, label, origin))

    return results


def _find_out_arrays(root: Any) -> List[List[Any]]:
    """Raccoglie tutte le liste associate alla chiave 'out' in obj."""
    return find_section(root, ['out']) or []


def _pair_out_arrays(out_arrays: List[List[Any]]) -> List[Tuple[int, Optional[List[Any]], Optional[List[Any]]]]:
    """
    Abbina array numerici a array di etichette come in _pair_in_arrays,
    minimizzando la differenza di lunghezza e preferendo la labels-list più lunga a parità.
    """
    numeric = [(i, a) for i, a in enumerate(out_arrays) if is_mostly_ints(a)]
    labels = [(i, a) for i, a in enumerate(out_arrays) if is_mostly_strings(a)]

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
