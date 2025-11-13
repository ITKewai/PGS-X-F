#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core_logic.py
-----------
Modulo che contiene la logica principale del programma, estratta da main.py.
Questo modulo è riutilizzabile sia dalla CLI che dal web server.
La logica è strutturata in funzioni e classi per facilitare l'uso da ambienti diversi.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from utils.yaml.data.core import make_axis_sys_addr, make_alarm_sys_addr
from utils.yaml.data.costants import AXIS_GROUPS_ORDER, ALARM_GROUPS_ORDER, SYSTEM_TYPE, SYSTEM_TYPE_REV
from utils.yaml.download import *
from utils.db.data_config import *


class SearchState:
    """Gestisce lo stato della ricerca e della configurazione caricata."""

    def __init__(self):
        self.current_config_path: Optional[Path] = None
        self.current_sn: str = ""
        self.config_loaded: bool = False
        self.search_results: List[str] = []

    def load_config(self, config_path: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Carica un file di configurazione YAML.
        Ritorna (success: bool, message: str)
        """
        try:
            if config_path is None:
                config_path = choose_and_prepare_config(self.current_sn)

            populate_from_yaml_file(config_path)
            self.current_config_path = config_path
            self.current_sn = data_config.Config_Header.get(HEADER_SN, "")
            self.config_loaded = True
            msg = f"Config caricato: {self.current_sn}"
            logging.info(msg)
            return True, msg
        except Exception as e:
            msg = f"Errore nel caricamento del config: {e}"
            logging.error(msg)
            return False, msg

    def search_io(self, io_type: int, io_number: int) -> List[str]:
        """
        Esegue una ricerca per un IO specifico.
        Ritorna una lista di stringhe con i risultati.
        """
        if not self.config_loaded:
            return ["Errore: Nessun config caricato"]

        try:
            results = run_io_search(iotype=io_type, Ind=io_number, verbose=False)
            self.search_results = results
            return results
        except Exception as e:
            logging.error(f"Errore nella ricerca: {e}")
            return [f"Errore nella ricerca: {e}"]

    def get_io_types(self) -> Dict[int, str]:
        """Ritorna il mapping tra tipo IO e descrizione."""
        return {
            1: "DI (Digital Input)",
            2: "AI (Analog Input)",
            3: "DO (Digital Output)",
            4: "AO (Analog Output)",
            5: "SYSTEM",
            6: "CHECK",
            7: "FREE (Scan automatico)"
        }

    def get_axis_list(self) -> List[Dict[str, any]]:
        """Ritorna la lista degli assi disponibili."""
        try:
            axis_nodes = data_config.Axis_Param
            result = []
            for i in range(min(len(axis_nodes), MAX_ASSE + 1)):
                name = get_axis_name(i) if i < len(data_config.Axis_Name) else f"axis[{i}]"
                result.append({"index": i, "name": name})
            return result
        except Exception as e:
            logging.error(f"Errore nel recupero degli assi: {e}")
            return []

    def get_alarm_list(self) -> List[Dict[str, any]]:
        """Ritorna la lista degli allarmi disponibili."""
        try:
            alarm_rows = data_config.Alarm_Param
            result = []
            for i, alarm in enumerate(alarm_rows):
                if i > MAX_ALARM:
                    break
                name = getattr(alarm, "name", None)
                if name not in (None, "", "x", "X"):
                    result.append({"index": i, "name": name})
            return result
        except Exception as e:
            logging.error(f"Errore nel recupero degli allarmi: {e}")
            return []

    def search_system(self, sys_type: str, index: int, field: str) -> Tuple[bool, str]:
        """
        Esegue una ricerca di sistema (AXIS o ALARM).
        Ritorna (success: bool, result_message: str)
        """
        if not self.config_loaded:
            return False, "Errore: Nessun config caricato"

        try:
            # Normalizza il tipo di sistema
            if sys_type.isdigit():
                type_id = int(sys_type)
                sys_type = SYSTEM_TYPE_REV.get(type_id)
                if not sys_type:
                    return False, "TYPE di sistema non valido"
            else:
                sys_type = sys_type.strip().upper()
                if sys_type not in SYSTEM_TYPE:
                    return False, "TYPE di sistema sconosciuto"

            if sys_type not in ("AXIS", "ALARM"):
                return False, f"TYPE '{sys_type}' non supportato (solo AXIS/ALARM)"

            # Normalizza il field
            fields = AXIS_GROUPS_ORDER if sys_type == "AXIS" else ALARM_GROUPS_ORDER
            if field.isdigit():
                fidx = int(field)
                if not (0 <= fidx < len(fields)):
                    return False, "FIELD index fuori range"
                field = fields[fidx]
            else:
                field = field.strip().upper()
                if field not in fields:
                    return False, "FIELD sconosciuto"

            # Calcola il numero di sistema
            if sys_type == "AXIS":
                number = make_axis_sys_addr(field, index)
            else:
                number = make_alarm_sys_addr(field, index)

            human = decode_sys_addr(number) or f"{sys_type}.{field}[{index}]"
            results = run_io_search(iotype=IO_DI, Ind=number, verbose=False)

            message = f"SYSTEM → {human} => numero: {number}\n"
            message += "\n".join(results) if results else "Nessun risultato"

            return True, message
        except Exception as e:
            logging.error(f"Errore nella ricerca di sistema: {e}")
            return False, f"Errore: {e}"
