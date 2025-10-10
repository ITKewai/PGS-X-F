#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from utils.version import __version__, __pgs_version__, __author__, __company__, __product__, __copyright__, get_version_info
from utils.yaml.data.io import *
from utils.yaml.data.params import *
from utils.yaml.download import *
from utils.yaml.load import *


def _pause_if_frozen():
    if getattr(sys, "frozen", False):  # eseguibile PyInstaller
        try:
            input("\nPremi Invio per chiudere...")
        except EOFError:
            pass


def main():
    print(get_version_info())
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
        tipo_opt = (1, 2, 3, 4, 5, 7)
        tipo_raw = input("Che tipo stai cercando? (1=DI, 2=AI, 3=DO, 4=AO, 5=SYSTEM, 7=FREE, Invio per uscire): ").strip().lower()
        # Invio -> torna al menu precedente (scelta config) e ricarica il YAML
        if tipo_raw == "":
            print("\n⤴️  Torno alla scelta del config...")
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
            # torna al menu dei tipi
            continue
        # forse lo riabiliterò
        # if tipo_raw in ("q", "quit", "exit", "esci"):
        #     print("Uscita.")
        #     _pause_if_frozen()
        #     return

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
            print("AI:")
            run_free_scan_ai(data)
            print("AO:")
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


