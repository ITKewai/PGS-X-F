from utils.yaml.data.input import *
from utils.yaml.data.humanize import *


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


def search_in_field_matches(obj_node: Any, target_number: int) -> List[Tuple[int, int, Optional[str], Optional[str]]]:
    """
    Cerca il numero 'target_number' all'interno degli array '- in:' dovunque nel documento.
    Preferisce l'etichetta dalla lista labels abbinata; se mancante/insufficiente/'x',
    usa la mappatura per indice (IN_INDEX_LABELS) per ricavare label e origine.
    Ritorna: (pair_id, index, label_opzionale, origine_opzionale)
    """
    results: List[Tuple[int, int, Optional[str], Optional[str]]] = []
    in_arrays = find_in_arrays(obj_node)
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
                label = label_from_in_index(idx)

            # 3) calcola l'origine
            origin = infer_in_origin(label) if label else origin_from_in_index(idx)

            results.append((pid, idx, label, origin))

    return results


def _pair_in_arrays(in_arrays: List[List[Any]]) -> List[Tuple[int, Optional[List[Any]], Optional[List[Any]]]]:
    numeric = [(i, a) for i, a in enumerate(in_arrays) if is_mostly_ints(a)]
    labels = [(i, a) for i, a in enumerate(in_arrays) if is_mostly_strings(a)]

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
