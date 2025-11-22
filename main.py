#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import sys

from utils.exe.config import load_exe_config
from utils.version import __version__, __pgs_version__, __author__, __company__, __product__, __copyright__, get_version_info
from utils.yaml.data.core import make_axis_sys_addr, make_alarm_sys_addr
from utils.yaml.data.costants import AXIS_GROUPS_ORDER, ALARM_GROUPS_ORDER, SYSTEM_TYPE, SYSTEM_TYPE_REV
from utils.yaml.download import *
# from utils.yaml.data.params import *
from utils.db.data_config import *

sn = ''


def _pause_if_frozen():
    """Se eseguibile PyInstaller, pausa prima di chiudere."""
    if getattr(sys, "frozen", False):
        try:
            input("\nPremi Invio per chiudere...")
        except EOFError:
            pass


def print_in_columns(entries: list[str], cols: int = 3) -> None:
    """Stampa una lista di stringhe in colonne."""
    if not entries:
        return
    colw = max(len(s) for s in entries) + 2
    for i in range(0, len(entries), cols):
        row = entries[i:i + cols]
        logging.info("  " + "".join(s.ljust(colw) for s in row))


def main():
    """
    Modalità CLI tradizionale.
    Mantiene la logica originale del programma.
    """
    global sn

    logging.info(get_version_info())

    config = load_exe_config()

    cfg_path = choose_and_prepare_config(sn)

    try:
        populate_from_yaml_file(cfg_path)
    except Exception as e:
        logging.critical(f"Errore nel parsing YAML: {e}")
        _pause_if_frozen()
        return

    sn = data_config.Config_Header[HEADER_SN]
    logging.info(f"Caricato config della commessa: {data_config.Config_Header[HEADER_SN]}")

    # 2) Loop interattivo: ripeti la domanda dopo ogni ricerca
    while True:
        logging.info("\n" + "-" * 60)
        tipo_opt = (1, 2, 3, 4, 5, 6, 7)
        tipo_raw = input("Che tipo stai cercando? (1=DI, 2=AI, 3=DO, 4=AO, 5=SYSTEM, 6=CHECK, 7=FREE, Invio per uscire): ").strip().lower()
        # Invio -> torna al menu precedente (scelta config) e ricarica il YAML
        if tipo_raw == "":
            logging.info("-" * 60)
            cfg_path = choose_and_prepare_config(sn)
            try:
                populate_from_yaml_file(cfg_path)
            except Exception as e:
                logging.info(f"Errore nel parsing YAML: {e}")
                _pause_if_frozen()
                return
            sn = data_config.Config_Header[HEADER_SN]
            logging.info(f"Caricato config della commessa: {data_config.Config_Header[HEADER_SN]}")
            # torna al menu dei tipi
            continue
        # forse lo riabiliterò
        # if tipo_raw in ("q", "quit", "exit", "esci"):
        #     logging.info("Uscita.")
        #     _pause_if_frozen()
        #     return

        try:
            tipo = int(tipo_raw)
        except ValueError:
            logging.info("Tipo non valido. Inserisci 1, 2, 3, 4, 5 o 7.")
            continue

        if tipo not in tipo_opt:
            logging.info("Tipo non valido. Usa 1=DI, 2=AI, 3=DO, 4=AO, 5=SYSTEM, 7=FREE.")
            continue

        logging.info("-" * 60)

        # ====================== SYSTEM (nessuna richiesta numero qui) ======================
        if tipo == 5:
            # --- SYSTEM lookup: scegli TYPE -> INDEX -> FIELD, calcola numero e cerca nei DI ---
            logging.info("Scegli il TYPE di sistema (nome o numero):")
            entries = [f"{val} = {name}" for name, val in sorted(SYSTEM_TYPE.items(), key=lambda kv: kv[1])]
            print_in_columns(entries, cols=4)
            sel = input("TYPE: ").strip()

            # Normalizzo la scelta (accetta sia numero sia nome)
            if sel.isdigit():
                type_id = int(sel)
                sys_type = SYSTEM_TYPE_REV.get(type_id)
                if not sys_type:
                    logging.info("TYPE non valido.")
                    continue
            else:
                sys_type = sel.strip().upper()
                if sys_type not in SYSTEM_TYPE:
                    logging.info("TYPE non valido.")
                    continue

            if sys_type not in ("AXIS", "ALARM"):
                logging.info(f"TYPE '{sys_type}' non ancora supportato qui (solo AXIS/ALARM).")
                continue

            # --- Prima di chiedere l'indice, mostra mappa indice -> nome ---
            if sys_type == "AXIS":
                axis_nodes = data_config.Axis_Param

                def axis_name(i: int) -> str:
                    try:
                        return get_axis_name(i)
                    except Exception:
                        return f"axis[{i}]"

                n_to_show = min(len(axis_nodes), MAX_ASSE + 1)

                logging.info("\nMappa AXIS (indice → nome):")
                # prepara le stringhe "[ii] nome"
                entries = [f"[{i:02d}] {axis_name(i)}" for i in range(n_to_show)]
                if entries:
                    cols = 6
                    colw = max(len(s) for s in entries) + 2
                    for k in range(0, len(entries), cols):
                        row = entries[k:k + cols]
                        logging.info("  " + "".join(s.ljust(colw) for s in row))

                if n_to_show < MAX_ASSE + 1:
                    logging.info(f"... (definiti {n_to_show} assi su {MAX_ASSE + 1})")

                idx_prompt_max = MAX_ASSE
            else:  # ALARM
                alarm_rows = data_config.Alarm_Param
                logging.info("\nAlcuni ALARM definiti (indice → nome):")
                for i, alarm in enumerate(alarm_rows):
                    try:
                        name = getattr(alarm, "name", None)
                        if name not in (None, "", "x", "X"):
                            logging.info(f"  [{i:03d}] {name}")
                    except Exception:
                        continue

                if len(alarm_rows) < MAX_ALARM + 1:
                    logging.info(f"(presenti {len(alarm_rows)} allarmi; range massimo supportato 0..{MAX_ALARM})")

                idx_prompt_max = MAX_ALARM

            # --- Scelta INDEX con validazione ---
            try:
                idx_raw = input(f"\nInserisci INDEX per {sys_type} (0..{idx_prompt_max}): ").strip()
                index = int(idx_raw)
            except TypeError as e:
                logging.critical(f"INDEX non valido: {e}")
                continue

            # --- Scelta FIELD (nome o indice) ---
            fields = AXIS_GROUPS_ORDER if sys_type == "AXIS" else ALARM_GROUPS_ORDER

            logging.info(f"\nScegli FIELD per {sys_type} (nome o indice):")
            entries = [f"[{i:02d}] {name}" for i, name in enumerate(fields)]
            print_in_columns(entries, cols=3)

            fsel = input("FIELD: ").strip()

            if fsel.isdigit():
                fidx = int(fsel)
                if not (0 <= fidx < len(fields)):
                    logging.info("FIELD index fuori range.")
                    continue
                field = fields[fidx]
            else:
                field = fsel.strip().upper()
                if field not in fields:
                    logging.info("FIELD sconosciuto.")
                    continue

            # --- Calcolo del numero di sistema ---
            try:
                if sys_type == "AXIS":
                    number = make_axis_sys_addr(field, index)
                else:  # ALARM
                    number = make_alarm_sys_addr(field, index)
            except Exception as e:
                logging.info(f"Errore nel calcolo dell'indirizzo di sistema: {e}")
                continue

            human = decode_sys_addr(number) or f"{sys_type}.{field}[{index}]"
            logging.info(f"\nSYSTEM → {human}  => numero: {number}")
            run_io_search(iotype=IO_DI, Ind=number, verbose=True)
            continue

        if tipo == 6:
            custom_function()
            continue
        # ==================== /SYSTEM ====================

        # ====================== FREE (scan automatico) ======================
        if tipo == 7:
            logging.info("DI:")
            run_free_scan(IO_DI)
            logging.info("DO:")
            run_free_scan(IO_DO)
            logging.info("AI:")
            run_free_scan(IO_AI)
            logging.info("AO:")
            run_free_scan(IO_AO)
            logging.info("RI:")
            run_free_scan(IO_RI)
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
                    logging.info("Numero non valido. Riprova (Invio per tornare al menu).")
                    continue

                logging.info("-" * 60)
                if tipo == 1:
                    run_io_search(iotype=IO_DI, Ind=target_number, verbose=True)
                elif tipo == 2:
                    run_io_search(iotype=IO_AI, Ind=target_number, verbose=True)
                elif tipo == 3:
                    run_io_search(iotype=IO_DO, Ind=target_number, verbose=True)
                elif tipo == 4:
                    run_io_search(iotype=IO_AO, Ind=target_number, verbose=True)
            continue


if __name__ == "__main__":
    cfg = load_exe_config()
    if cfg.get("webServer", False):
        # modalità web
        from utils.web.server import app
        try:
            app.run(host="0.0.0.0", port=5000, debug=cfg.get("debug", False))
        except Exception as e:
            logging.error(f"\n[Errore inatteso]: {e}")
            _pause_if_frozen()
        sys.exit(1)
    else:
        try:
            main()
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
            if code not in (0, None):
                logging.info(f"\n[EXIT] Codice: {code}")
            _pause_if_frozen()
            sys.exit(code)
        except Exception as e:
            logging.error(f"\n[Errore inatteso]: {e}")
            _pause_if_frozen()
            sys.exit(1)
