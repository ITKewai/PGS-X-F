from typing import Any, List, Tuple, Optional, Dict
from utils.yaml.data.costants import *
from utils.yaml.data.feedback import *
from utils.yaml.data.input import *
from utils.yaml.data.output import *
from utils.yaml.data.motors import *
from utils.yaml.data.alarm_maintenance import *
from utils.yaml.data.core import *
from utils.yaml.data.axis import *
from utils.yaml.data.params import *

"""
Digital Input
"""


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
    axis_int_lists = find_axis_int_lists(data.get('obj'))
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

"""
Digital Output
"""
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

"""
Analog Input
"""
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

    # Campi STATUS dei -obj.output
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


def search_ai_in_ao_matches(ao_list: List[list], target_number: int, only_bus: bool = True) -> List[Tuple[int, str, Optional[str]]]:
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


"""
Analog Output
"""


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


"""
RI
"""


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
