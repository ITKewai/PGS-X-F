# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/db/data_config.py
---------------------------------
Replica in Python la deserializzazione del config YAML (ristrutturato da load_yaml)
verso l'istanza DATA_CONFIG, seguendo la logica SCL.
"""
from __future__ import annotations
import logging
import sys
import json
import math

from pathlib import Path
from typing import Any, List, Dict, Sequence, Optional, Tuple

from utils.exe.config import load_exe_config
from utils.exports.tia_constants_map import *
from utils.version import get_pgsx_version
from utils.yaml.data.core import make_axis_sys_addr
from utils.yaml.data.costants import BASE_AXIS, AXIS_GROUP_STEP, ALARM_GROUP_STEP, AXIS_GROUPS_ORDER, SYSTEM_TYPE, \
    ALARM_GROUPS_ORDER
from utils.yaml.load import load_yaml
from utils.exports.tia_constants import *  # noqa: F401,F403  (porta DATA_CONFIG, MAX_*, costanti simboliche, UDT, ecc.)
from utils.exports.tia_constants import __version__ as ver
# 🎨 Codici colore ANSI
RESET = "\033[0m"
GRAY = "\033[90m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD_RED = "\033[1;91m"


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: GRAY,
        logging.INFO: RESET,  # INFO resta normale
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, RESET)
        msg = super().format(record)
        return f"{color}{msg}{RESET}"


# ⚙️ Configurazione handler con formatter colorato
handler = logging.StreamHandler(sys.stdout)
# handler.setFormatter(ColorFormatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
handler.setFormatter(ColorFormatter("%(message)s", "%H:%M:%S"))
# handler.setFormatter(ColorFormatter())

config = load_exe_config()

log_level = logging.DEBUG if config['debug'] else logging.INFO

logging.basicConfig(level=log_level, handlers=[handler])

logger = logging.getLogger(__name__)  # crea un logger con il nome del file

# logging.debug("Messaggio di debug (non verrà mostrato)")
# logging.info("Avvio programma")
# logging.warning("Attenzione: parametro mancante")
# logging.error("Errore di connessione")
# logging.critical("Errore critico! Arresto immediato")
# Istanza globale popolata dalla deserializzazione
logger.debug('IN: building data_config class')
data_config: DATA_CONFIG = DATA_CONFIG()  # type: ignore[name-defined]
logger.debug('OUT: loading data_config class')

data_config.IO_DI_List: list[Type_IOParam] = []
data_config.IO_DO_List: list[Type_IOParam] = []
data_config.IO_AI_List: list[Type_IOParam] = []
data_config.IO_AO_List: list[Type_IOParam] = []
data_config.IO_RI_List: list[Type_IOParam] = []


# ------------------------------
# Public API
# ------------------------------
def populate_from_yaml_file(yaml_path: Path | str) -> None:
    logging.debug('IN: populate_from_yaml_file')
    p = Path(yaml_path).resolve()
    data = load_yaml(str(p))
    if not isinstance(data, dict):
        logging.critical("Il YAML caricato non è un dict.")
        raise ValueError("Il YAML deve essere un dict.")
    deserialize_config(data)
    logging.debug('OUT: populate_from_yaml_file')


def deserialize_config(data: Dict[str, Any]) -> None:
    logger.debug('IN: deserialize_config')
    _clean_data_config()
    _deserialize_UM(data)  # UM / UMT
    _deserialize_header(data)
    _deserialize_card_exc(data)  # card / exc
    _deserialize_axind_in_out(data)  # axind / in / out (indici mapping rapidi)
    _deserialize_io(data)  # di / ai / do / ao / ri   (da data['io'])
    _deserialize_obj_axis(data)  # axis/bool/int/real/type  (da data['obj']['axis'])
    _deserialize_obj_input(data)  # input                    (da data['obj']['input'])
    _deserialize_obj_output(data)  # output                   (da data['obj']['output'])
    _deserialize_obj_fb(data)  # fb                       (da data['obj']['fb'])
    _deserialize_obj_pid(data)  # pid                      (da data['obj']['pid'] se presente)
    _deserialize_obj_mot(data)  # mot                      (da data['obj']['mot'])
    _deserialize_obj_alarm(data)  # alarm                    (da data['obj']['alarm'])
    _deserialize_obj_maint(data)  # maint                    (da data['obj']['maint'])
    _deserialize_obj_toolset(data)  # toolset                  (da data['obj']['toolset'])
    _finalize_config(data)
    _build_io_lists()
    logger.debug('OUT: deserialize_config')


# ------------------------------
# Helpers
# ------------------------------
def _as_list(seq: Any) -> List[Any]:
    if seq is None:
        return []
    if isinstance(seq, list):
        return seq
    return [seq]


def _to_int(x: Any, default: int = 0) -> int:
    try:
        if isinstance(x, (int, float)):
            return int(x)
        return int(str(x).strip())
    except Exception:
        return default


def _to_float(x: Any, default: float = 0.0) -> float:
    try:
        if isinstance(x, (int, float)):
            return float(x)
        return float(str(x).strip().replace(",", "."))
    except Exception:
        return default


def _bool_from_int(x: Any) -> bool:
    return _to_int(x, 0) == 1


def _reset_udt_array(arr) -> None:
    """Chiama .reset() su ogni elemento di un array UDT, se presente."""
    if not arr:
        return
    for x in arr:
        if hasattr(x, "reset"):
            x.reset()


def _reset_all_defaults() -> None:
    """Usa i reset() generati in tia_constants per riportare ai defaults gli array UDT dentro data_config."""
    udt_arrays = [
        "IO_Param",
        "Axis_Param",
        "Input_Param",
        "Output_Param",
        "Feedback_Param",
        "PID_Param",
        "Motor",
        "Alarm_Param",
        "Maint_Param",
        "Toolset_Param",
    ]
    for name in udt_arrays:
        _reset_udt_array(getattr(data_config, name, []))


def _clean_data_config() -> None:
    """
    Pulisce completamente data_config:
    1) resetta gli UDT agli _defaults via .reset()
    2) normalizza campi runtime dove i defaults non bastano
    3) svuota le liste helper IO_*_List
    """
    logging.debug('IN: _clean_data_config')
    # 1️⃣ resetta tutto ai defaults
    if hasattr(data_config, "reset") and callable(getattr(data_config, "reset")):
        data_config.reset()
    else:
        _reset_all_defaults()

    # 2️⃣ Normalizzazioni extra
    # IO_Name: None → ""
    io_name = getattr(data_config, "IO_Name", None)
    if isinstance(io_name, list):
        for i in range(len(io_name)):
            if io_name[i] is None:
                io_name[i] = ""

    # DATA_ALARMS
    if hasattr(data_config, "DATA_ALARMS"):
        da = data_config.DATA_ALARMS
        max_warn = getattr(data_config, "MAX_WARNING", 0)
        if hasattr(da, "Ind"):
            da.Ind = [-1] * (max_warn + 1)
        if hasattr(da, "Cod"):
            da.Cod = [0] * (max_warn + 1)

    # RecyclingMotorInd
    if hasattr(data_config, "RecyclingMotorInd"):
        data_config.RecyclingMotorInd = -1

    # --- ✅ Stop arrays ---
    max_stop = getattr(data_config, "MAX_STOP", 0)
    if hasattr(data_config, "Stop_Ind"):
        data_config.Stop_Ind = [-1] * (max_stop + 1)
    if hasattr(data_config, "Stop_Name"):
        data_config.Stop_Name = [""] * (max_stop + 1)
    for stop_attr in ("Stop_DI", "Stop_DO", "Stop_AI", "Stop_AO", "Stop_RI"):
        if hasattr(data_config, stop_attr):
            setattr(data_config, stop_attr, [-1] * (max_stop + 1))

    # 2c) pulisci cache/dizionari runtime
    for maybe_map in (
            "IO_IndexMap",
            "IO_NameToIndex",
            "AxisNameToIndex",
            "DecodeCache",
            "IO_SearchCache",
    ):
        obj = getattr(data_config, maybe_map, None)
        if isinstance(obj, dict):
            obj.clear()

    # 3️⃣ svuota le liste helper (non nel TIA DB)
    data_config.IO_DI_List = []
    data_config.IO_DO_List = []
    data_config.IO_AI_List = []
    data_config.IO_AO_List = []
    data_config.IO_RI_List = []
    logging.debug('OUT: _clean_data_config')


def _deserialize_UM(data: Dict[str, Any]) -> None:
    for i in range(MAX_UM + 1):
        data_config.UM_FC[i] = data_config.UM_FC_Met[i]
        data_config.UM_Offset[i] = data_config.UM_Offset_Met[i]
        data_config.UM_NDec[i] = data_config.UM_NDec_Met[i]
        data_config.UM_Name[i] = data_config.UM_Name_Met[i]


# ------------------------------
# Header / Card / AxInd
# ------------------------------
def _deserialize_header(data: Dict[str, Any]) -> None:
    """ header / pstring / pbool / pint / preal / ptype — compatibile con YAML dove 'param' è lista di dizionari """
    logging.debug('IN: _deserialize_header')
    header = _as_list(data.get("header"))
    logger.debug(f"header: {header}")

    # Prepara Config_Header
    max_len = getattr(data_config, "MAX_HEADER", len(header))  # TODO: leggere dal file
    if len(data_config.Config_Header) <= max_len:
        data_config.Config_Header = [0] * (max_len + 1)
    for i in range(max_len + 1):
        data_config.Config_Header[i] = _to_int(header[i]) if i < len(header) else 0

    # --- Parsing 'param' (lista di dizionari nel tuo YAML) ---
    raw_param = data.get("param", [])
    param = {}

    # Supporta lista di dict come nel tuo YAML
    if isinstance(raw_param, list):
        for entry in raw_param:
            if isinstance(entry, dict):
                param.update(entry)
    elif isinstance(raw_param, dict):
        param = raw_param

    # Ora param è un dict come {"pstring": [...], "pbool": [...], ...}
    pstring = _as_list(param.get("pstring"))
    pbool = _as_list(param.get("pbool"))
    pint = _as_list(param.get("pint"))
    preal = _as_list(param.get("preal"))
    ptype = _as_list(param.get("ptype"))

    logger.debug(f"pstring: {pstring}")
    logger.debug(f"pbool: {pbool}")
    logger.debug(f"pint: {pint}")
    logger.debug(f"preal: {preal}")
    logger.debug(f"ptype: {ptype}")

    # --- pstring ---
    max_len = getattr(data_config, "MAX_PARAMSTRING", len(pstring))  # TODO: leggere dal file
    if len(data_config.ParamString) <= max_len:
        data_config.ParamString = [""] * (max_len + 1)
    for i in range(max_len + 1):
        data_config.ParamString[i] = str(pstring[i]) if i < len(pstring) else ""

    # --- pbool ---
    max_len = getattr(data_config, "MAX_PARAMBOOL", len(pbool))  # TODO: leggere dal file
    if len(data_config.ParamBool) <= max_len:
        data_config.ParamBool = [False] * (max_len + 1)
    for i in range(max_len + 1):
        data_config.ParamBool[i] = _bool_from_int(pbool[i]) if i < len(pbool) else False

    # --- pint ---
    max_len = getattr(data_config, "MAX_PARAMINT", len(pint))  # TODO: leggere dal file
    if len(data_config.ParamInt) <= max_len:
        data_config.ParamInt = [0] * (max_len + 1)
    for i in range(max_len + 1):
        data_config.ParamInt[i] = _to_int(pint[i]) if i < len(pint) else 0

    # --- preal ---
    max_len = getattr(data_config, "MAX_PARAMREAL", len(preal))  # TODO: leggere dal file
    if len(data_config.ParamReal) <= max_len:
        data_config.ParamReal = [0.0] * (max_len + 1)
        data_config.ParamRealCfg = [0.0] * (max_len + 1)
    for i in range(max_len + 1):
        val = _to_float(preal[i]) if i < len(preal) else 0.0
        data_config.ParamRealCfg[i] = val
        data_config.ParamReal[i] = val

    # --- ptype ---
    max_len = getattr(data_config, "MAX_PARAMREAL", len(ptype))  # TODO: leggere dal file
    if len(data_config.ParamRealType) <= max_len:
        data_config.ParamRealType = [-1] * (max_len + 1)
    for i in range(max_len + 1):
        data_config.ParamRealType[i] = _to_int(ptype[i], -1) if i < len(ptype) else -1
    logging.debug('OUT: _deserialize_header')


def _deserialize_card_exc(data: Dict[str, Any]) -> None:
    """ card / exc → struttura SDO se presente """
    logging.debug('IN: _deserialize_card_exc')
    card = _as_list(data.get("card"))
    for idx, row in enumerate(card):
        if not isinstance(row, (list, tuple)):
            continue
        if not hasattr(data_config, "DATA_SDO"):
            break
        try:
            data_config.DATA_SDO.SdoIFM.ARRAY_IFM[idx].NODO = 101 + idx
            data_config.DATA_SDO.SdoIFM.ARRAY_IFM[idx].TIPO = _to_int(row[0], -1)
            data_config.DATA_SDO.SdoIFM.ARRAY_IFM[idx].DITHER_FREQ = _to_int(row[1], 0)
            data_config.DATA_SDO.SdoIFM.ARRAY_IFM[idx].DITHER_VALUE = _to_int(row[2], 0)
        except Exception:
            pass

    exc = _as_list(data.get("exc"))
    for idx, row in enumerate(exc):
        if not isinstance(row, (list, tuple)):
            continue
        if not hasattr(data_config, "DATA_SDO"):
            break
        try:
            data_config.DATA_SDO.SdoIFM.ARRAY_SPECIALI[idx].ID = _to_int(row[0], 0)
            data_config.DATA_SDO.SdoIFM.ARRAY_SPECIALI[idx].N_OUT = _to_int(row[1], 0)
            data_config.DATA_SDO.SdoIFM.ARRAY_SPECIALI[idx].DITHER_FREQ = _to_int(row[2], 0)
            data_config.DATA_SDO.SdoIFM.ARRAY_SPECIALI[idx].DITHER_VALUE = _to_int(row[3], 0)
        except Exception:
            pass
    logging.debug('OUT: _deserialize_card_exc')


def _deserialize_axind_in_out(data: Dict[str, Any]) -> None:
    """ axind / in / out """
    logging.debug('IN: _deserialize_axind_in_out')
    axind = _as_list(data.get("axind"))
    limit = min(len(data_config.AxisFunInd), getattr(data_config, "MAX_ASSEFUNIND", len(axind)) + 1)  # TODO: leggere dal file
    for i in range(limit):
        data_config.AxisFunInd[i] = _to_int(axind[i]) if i < len(axind) else -1

    in_list = _as_list(data.get("in"))
    limit = min(len(data_config.InInd), getattr(data_config, "MAX_STATOBOOL", len(in_list)) + 1)  # TODO: leggere dal file
    for i in range(limit):
        data_config.InInd[i] = _to_int(in_list[i], -1) if i < len(in_list) else -1

    out_list = _as_list(data.get("out"))
    limit = min(len(data_config.OutInd), getattr(data_config, "MAX_STATOBOOL", len(out_list)) + 1)  # TODO: leggere dal file
    for i in range(limit):
        data_config.OutInd[i] = _to_int(out_list[i], -1) if i < len(out_list) else -1
    logging.debug('OUT: _deserialize_axind_in_out')


# ------------------ IO (di/ai/do/ao/ri) ------------------
def _valid_io_rows(io_data: Dict[str, Any], field: str) -> List[Sequence[Any]]:  # DYNAMIC PATHING
    rows = _as_list(io_data.get(field))
    out = []
    for row in rows:
        if row is None:
            continue
        if not isinstance(row, (list, tuple)) or len(row) == 0:
            continue
        out.append(row)
    return out


def _prepare_io_layout(io_data: Dict[str, Any]) -> Dict[str, List[Sequence[Any]]]:  # DYNAMIC PATHING
    fields = ("di", "ai", "do", "ao", "ri")
    counts, starts, valid = {}, {}, {}
    # 1) filtra righe valide per ciascun field
    for f in fields:
        valid[f] = _valid_io_rows(io_data, f)
        counts[f] = len(valid[f])
    # 2) calcola gli start cumulativi
    acc = 0
    for f in fields:
        starts[f] = acc
        acc += counts[f]
    # 3) salva su data_config per uso globale
    data_config.IO_COUNTS = counts
    data_config.IO_STARTS = starts
    data_config.IO_TOTAL = acc
    return valid


def _iotype_to_field(iotype: int) -> Optional[str]:  # DYNAMIC PATHING
    if iotype == IO_DI: return "di"
    if iotype == IO_AI: return "ai"
    if iotype == IO_DO: return "do"
    if iotype == IO_AO: return "ao"
    if iotype == IO_RI: return "ri"
    return None


# def _deserialize_io(data: Dict[str, Any]) -> None:   # DYNAMIC PATHING
#     # data['io'] è un dict: {'di': [[...], ...], 'ai': [...], ...}
#     io_data = data.get("io", {})
#     counts = {field: 0 for field in ("di", "ai", "do", "ao", "ri")}
#     for field in ("di", "ai", "do", "ao", "ri"):
#         rows = _as_list(io_data.get(field))
#         for ind, row in enumerate(rows):
#             if row is None:
#                 continue
#             if not isinstance(row, (list, tuple)) or len(row) == 0:
#                 continue
#             _deserialize_io_row(field, ind, row)
#             counts[field] += 1
#     logger.info(f"Rilevati IO: DI={counts['di']}, AI={counts['ai']}, DO={counts['do']}, AO={counts['ao']}, RI={counts['ri']}")

def _deserialize_io(data: Dict[str, Any]) -> None:  # DYNAMIC PATHING
    logger.debug('IN: _deserialize_io')
    io_data = data.get("io", {}) or {}
    # Pre-scan: layout dinamico e righe già filtrate
    valid_rows = _prepare_io_layout(io_data)
    counts = {k: len(v) for k, v in valid_rows.items()}

    # Deserializza usando gli offset dinamici
    for field in ("di", "ai", "do", "ao", "ri"):
        rows = valid_rows[field]
        for ind, row in enumerate(rows):
            _deserialize_io_row(field, ind, row)

    logger.info(f"Rilevati IO: DI={counts['di']}, AI={counts['ai']}, DO={counts['do']}, AO={counts['ao']}, RI={counts['ri']}")
    logger.debug('OUT: _deserialize_io')


def _io_global_index(field: str, ind: int) -> int:
    # Dinamico se il layout è disponibile
    starts = getattr(data_config, "IO_STARTS", None)
    counts = getattr(data_config, "IO_COUNTS", None)
    if isinstance(starts, dict) and isinstance(counts, dict) and field in starts:
        return starts[field] + ind
    logging.critical("Layout IO non disponibile, uso costante PLC con MAX_*.")
    # Fallback: vecchia logica con MAX_*
    if field == "di":
        return ind
    if field == "ai":
        return (MAX_DI + 1) + ind
    if field == "do":
        return (MAX_AI + 1) + (MAX_DI + 1) + ind
    if field == "ao":
        return (MAX_DO + 1) + (MAX_AI + 1) + (MAX_DI + 1) + ind
    if field == "ri":
        return (MAX_AO + 1) + (MAX_DO + 1) + (MAX_AI + 1) + (MAX_DI + 1) + ind
    return ind


def _deserialize_io_row(field: str, ind: int, row: Sequence[Any]) -> None:
    # logging.debug(f'IN: _deserialize_io_row: field={field}, ind={ind}')
    k = _io_global_index(field, ind)
    if k > getattr(data_config, "MAX_IO", k):
        return

    # row: [Name, bool..., int..., dint..., real..., exprint..., exprreal...]
    name = str(row[0])
    data_config.IO_Name[k] = name
    # logging.debug(f"_deserialize_io_row: field={field}, ind={ind}, global_index={k}, name={name}")
    try:
        data_config.IO_Param[k].iotype = {
            "di": getattr(data_config, "IO_DI", 0),
            "ai": getattr(data_config, "IO_AI", 1),
            "do": getattr(data_config, "IO_DO", 2),
            "ao": getattr(data_config, "IO_AO", 3),
            "ri": getattr(data_config, "IO_RI", 4),
        }[field]
    except Exception:
        pass
    data_config.IO_Param[k].name = name

    first = 1
    # Bool
    for j in range(MAX_IOBOOL + 1):
        val = row[first + j] if first + j < len(row) else 0
        data_config.IO_Param[k].boolval[j] = _bool_from_int(val)
    first += (MAX_IOBOOL + 1)

    # Int
    for j in range(MAX_IOINT + 1):
        val = row[first + j] if first + j < len(row) else 0
        data_config.IO_Param[k].intval[j] = _to_int(val)
    first += (MAX_IOINT + 1)

    # DInt
    for j in range(MAX_IODINT + 1):
        val = row[first + j] if first + j < len(row) else 0
        data_config.IO_Param[k].dintval[j] = _to_int(val)  # YAML stringhe -> int
    first += (MAX_IODINT + 1)

    # Real
    for j in range(MAX_IOREAL + 1):
        val = row[first + j] if first + j < len(row) else 0.0
        fv = _to_float(val)
        data_config.IO_Param[k].realvalcfg[j] = fv
        data_config.IO_Param[k].realval[j] = fv

    # EXPRINT / EXPRREAL opzionali (TYPEVERSION >= 25)
    typever = 0
    try:
        typever = int(data_config.Config_Header[getattr(data_config, "HEADER_TYPEVERSION", 0)])
    except Exception:
        pass

    if typever >= 25:
        first += (MAX_IOREAL + 1)
        if first < len(row):
            data_config.IO_Param[k].exprintval[0] = _to_int(row[first], -1)
            if data_config.IO_Param[k].exprintval[0] >= 0:
                for j in range(1, MAX_EXPRINT + 1):
                    val = row[first + j] if first + j < len(row) else -1
                    data_config.IO_Param[k].exprintval[j] = _to_int(val, -1)
                # exprreal: MAX_EXPROPER + 1 valori
                first += MAX_EXPRINT
                for j in range(MAX_EXPROPER + 1):
                    val = row[first + j] if first + j < len(row) else 0.0
                    if hasattr(data_config.IO_Param[k], "exprrealval"):
                        data_config.IO_Param[k].exprrealval[j] = _to_float(val, 0.0)
                    else:
                        logging.debug(f"IO_Param[{k}] non ha exprrealval in questa versione")  # TODO: gestire meglio
        else:
            # default EXPRINT a -1
            for j in range(MAX_EXPRINT + 1):
                data_config.IO_Param[k].exprintval[j] = -1
    else:
        for j in range(MAX_EXPRINT + 1):
            data_config.IO_Param[k].exprintval[j] = -1

    # if data_config.IO_Param[k].intval[IO_INT_ADDRTYPE] == IO_TYPE_PNET:
    #     if field in ("ai", "ao"):
    #         DATA_STATUS.IO[k].Ind = data_config.IO_Param[k].intval[IO_INT_ADDR1]
    #     else:
    #         a1 = data_config.IO_Param[k].intval[IO_INT_ADDR1]
    #         a2 = data_config.IO_Param[k].intval[IO_INT_ADDR2]
    #         DATA_STATUS.IO[k].Ind = a1 * 8 + a2
    #
    # elif data_config.IO_Param[k].intval[IO_INT_ADDRTYPE] == IO_TYPE_SW:
    #     DATA_STATUS.IO[k].Ind = data_config.HMIAdd0 + data_config.IO_Param[k].intval[IO_INT_ADDR1]
    # elif data_config.IO_Param[k].intval[IO_INT_ADDRTYPE] >= IO_TYPE_NONE:
    #     DATA_STATUS.IO[k].Ind = -1
    # else:
    #     DATA_STATUS.IO[k].Ind = -1
    # logging.debug(f'OUT: _deserialize_io_row: field={field}, ind={ind}')


def _build_io_lists():
    logging.debug('IN: _build_io_lists')
    for param in data_config.IO_Param:
        if param.iotype == IO_DI:
            data_config.IO_DI_List.append(param)
        elif param.iotype == IO_DO:
            data_config.IO_DO_List.append(param)
        elif param.iotype == IO_AI:
            data_config.IO_AI_List.append(param)
        elif param.iotype == IO_AO:
            data_config.IO_AO_List.append(param)
        elif param.iotype == IO_RI:
            data_config.IO_RI_List.append(param)
    logger.debug(f'DI: {len(data_config.IO_DI_List)}, DO: {len(data_config.IO_DO_List)}, AI: {len(data_config.IO_AI_List)}, AO: {len(data_config.IO_AO_List)}, RI: {len(data_config.IO_RI_List)}, ')
    logging.debug('OUT: _build_io_lists')

# ------------------ OBJ/AXIS ------------------
def _deserialize_obj_axis(data: Dict[str, Any]) -> None:
    """
    Deserializza i blocchi 'axis' dal YAML e popola correttamente
    tutti i campi di data_config.Axis_Param[i] (boolval, intval, realval, fcval, offsetval, typval)
    in base agli indici standard definiti in Type_AxisParam.
    """
    logging.debug('IN: _deserialize_obj_axis')
    axis_blocks = data.get("obj", {}).get("axis", [])
    if not axis_blocks:
        return

    for ind, block in enumerate(axis_blocks):
        # ======================
        # 📌 Nome asse
        # ======================
        axis_row = _as_list(block.get("axis"))
        name = str(axis_row[0]) if axis_row else f"AXIS_{ind}"
        data_config.Axis_Name[ind] = name
        data_config.Axis_Param[ind].name = name
        try:
            data_config.DATA_STATUS_OUT.Axis_Name[ind] = name
        except Exception:
            pass

        # ======================
        # 📌 Boolval[0..MAX_ASSEBOOL]
        # ======================
        bool_list = _as_list(block.get("bool"))
        for j in range(min(len(bool_list), MAX_ASSEBOOL + 1)):  # TODO: leggere dal file
            data_config.Axis_Param[ind].boolval[j] = _bool_from_int(bool_list[j])
        # se meno valori → il resto default False
        for j in range(len(bool_list), MAX_ASSEBOOL + 1):  # TODO: leggere dal file
            data_config.Axis_Param[ind].boolval[j] = False

        # ======================
        # 📌 Intval[0..MAX_ASSEINT]
        # ======================
        int_list = _as_list(block.get("int"))
        for j in range(min(len(int_list), MAX_ASSEINT + 1)):  # TODO: leggere dal file
            data_config.Axis_Param[ind].intval[j] = _to_int(int_list[j], -1)
        for j in range(len(int_list), MAX_ASSEINT + 1):  # TODO: leggere dal file
            data_config.Axis_Param[ind].intval[j] = -1

        # ======================
        # 📌 Realvalcfg / Realval / Fcval / Offsetval / Typval
        # ======================
        real_list = _as_list(block.get("real"))
        for j in range(min(len(real_list), MAX_ASSEREAL + 1)):  # TODO: leggere dal file
            fv = _to_float(real_list[j], 0.0)
            data_config.Axis_Param[ind].realvalcfg[j] = fv
            data_config.Axis_Param[ind].realval[j] = fv

        type_list = _as_list(block.get("type"))
        for j in range(min(len(type_list), MAX_ASSEREAL + 1)):  # TODO: leggere dal file
            data_config.Axis_Param[ind].typval[j] = type_list[j]

        # TODO: controllare
        # # Se ci sono meno valori real → completa con 0.0
        # for j in range(len(real_list), MAX_ASSEREAL + 1):
        #     data_config.Axis_Param[ind].realvalcfg[j] = 0.0
        #     data_config.Axis_Param[ind].realval[j] = 0.0
        #     data_config.Axis_Param[ind].typval[j] = 0
        #     data_config.Axis_Param[ind].fcval[j] = 1.0
        #     data_config.Axis_Param[ind].offsetval[j] = 0.0
    logging.debug('OUT: _deserialize_obj_axis')

# ------------------ INPUT / OUTPUT / FB / PID / MOT / ALARM / MAINT / TOOLSET ------------------
def _deserialize_obj_input(data: Dict[str, Any]) -> None:
    logging.debug('IN: _deserialize_obj_input')
    rows = _as_list(data.get("obj", {}).get("input"))
    for ind, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            continue
        # bool
        for j in range(MAX_INPUTBOOL + 1):
            val = row[j] if j < len(row) else 0
            data_config.Input_Param[ind].boolval[j] = _bool_from_int(val)
        # int
        off = (MAX_INPUTBOOL + 1)
        for j in range(MAX_INPUTINT + 1):
            val = row[off + j] if off + j < len(row) else 0
            data_config.Input_Param[ind].intval[j] = _to_int(val)
        # dint (cfg + value uguali)
        off += (MAX_INPUTINT + 1)
        for j in range(MAX_INPUTDINT + 1):
            val = row[off + j] if off + j < len(row) else 0
            iv = _to_int(val)
            data_config.Input_Param[ind].dintvalcfg[j] = iv
            data_config.Input_Param[ind].dintval[j] = iv
    logging.debug('OUT: _deserialize_obj_input')

def _deserialize_obj_output(data: Dict[str, Any]) -> None:
    logging.debug('IN: _deserialize_obj_output')
    rows = _as_list(data.get("obj", {}).get("output"))
    for ind, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            continue
        # int
        for j in range(MAX_OUTPUTINT + 1):
            val = row[j] if j < len(row) else 0
            data_config.Output_Param[ind].intval[j] = _to_int(val)
        # dint
        off = (MAX_OUTPUTINT + 1)
        for j in range(MAX_OUTPUTDINT + 1):
            val = row[off + j] if off + j < len(row) else 0
            data_config.Output_Param[ind].dintval[j] = _to_int(val)
        # real
        off += (MAX_OUTPUTDINT + 1)
        for j in range(MAX_OUTPUTREAL + 1):
            val = row[off + j] if off + j < len(row) else 0.0
            data_config.Output_Param[ind].realval[j] = _to_float(val)
    logging.debug('OUT: _deserialize_obj_output')


def _deserialize_obj_fb(data: Dict[str, Any]) -> None:
    logging.debug('IN: _deserialize_obj_fb')
    rows = _as_list(data.get("obj", {}).get("fb"))
    typever = int(data_config.Config_Header[getattr(data_config, "HEADER_TYPEVERSION", 0)]) if hasattr(data_config, "Config_Header") else 0
    for ind, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            continue
        # int
        for j in range(MAX_FEEDBACKINT + 1):
            val = row[j] if j < len(row) else 0
            data_config.Feedback_Param[ind].intval[j] = _to_int(val)
        # dint (v.22+)
        fboffset = 0
        if typever >= 22:
            for j in range(MAX_FEEDBACKDINT + 1):
                val = row[(MAX_FEEDBACKINT + 1) + j] if (MAX_FEEDBACKINT + 1 + j) < len(row) else 0
                data_config.Feedback_Param[ind].dintval[j] = _to_int(val)
            fboffset = (MAX_FEEDBACKDINT + 1)
        else:
            # default fallback come in SCL (valori costanti)
            FB_INT_TIPO = getattr(data_config, "FB_INT_TIPO", None)
            FB_AI2 = getattr(data_config, "FB_AI2", None)
            FB_DINT_INF = getattr(data_config, "FB_DINT_INF", None)
            FB_DINT_SUP = getattr(data_config, "FB_DINT_SUP", None)
            if FB_INT_TIPO is not None and FB_DINT_INF is not None and FB_DINT_SUP is not None:
                if data_config.Feedback_Param[ind].intval[FB_INT_TIPO] == FB_AI2:
                    data_config.Feedback_Param[ind].dintval[getattr(data_config, "FB_DINT_INF")] = -32000
                else:
                    data_config.Feedback_Param[ind].dintval[getattr(data_config, "FB_DINT_INF")] = 48
                data_config.Feedback_Param[ind].dintval[getattr(data_config, "FB_DINT_SUP")] = 32000
        # real
        for j in range(MAX_FEEDBACKREAL + 1):
            idx = (MAX_FEEDBACKINT + 1) + fboffset + j
            val = row[idx] if idx < len(row) else 0.0
            fv = _to_float(val)
            data_config.Feedback_Param[ind].realvalcfg[j] = fv
            data_config.Feedback_Param[ind].realval[j] = fv
    logging.debug('OUT: _deserialize_obj_fb')


def _deserialize_obj_pid(data: Dict[str, Any]) -> None:
    logging.debug('IN: _deserialize_obj_pid')
    rows = _as_list(data.get("obj", {}).get("pid"))
    for ind, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            continue
        for j in range(MAX_PIDREAL + 1):
            val = row[j] if j < len(row) else 0.0
            data_config.PID_Param[ind].realval[j] = _to_float(val)
    logging.debug('OUT: _deserialize_obj_pid')


def _deserialize_obj_mot(data: Dict[str, Any]) -> None:
    logging.debug('IN: _deserialize_obj_mot')
    rows = _as_list(data.get("obj", {}).get("mot"))
    # Reset RecyclingMotorInd a inizio
    try:
        data_config.DATA_STATUS.RecyclingMotorInd = -1
    except Exception:
        pass
    for ind, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            continue
        # 0..1 -> config/selectable
        data_config.Motor_Config[ind] = _bool_from_int(row[0]) if len(row) > 0 else False
        data_config.Motor_Selectable[ind] = _bool_from_int(row[1]) if len(row) > 1 else False
        # seq,opt,default
        data_config.Motor[ind].seq = _bool_from_int(row[2]) if len(row) > 2 else False
        data_config.Motor[ind].opt = _bool_from_int(row[3]) if len(row) > 3 else False
        data_config.Motor[ind].default = _bool_from_int(row[4]) if len(row) > 4 else False
        # indices & timeouts
        data_config.Motor_LSInd[ind] = _to_int(row[5]) if len(row) > 5 else -1
        data_config.Motor_LS2Ind[ind] = _to_int(row[6]) if len(row) > 6 else -1
        data_config.Motor_TRInd[ind] = _to_int(row[7]) if len(row) > 7 else -1
        data_config.Motor_CmdInd[ind] = _to_int(row[8]) if len(row) > 8 else -1
        data_config.Motor_StatInd[ind] = _to_int(row[9]) if len(row) > 9 else -1
        data_config.Motor[ind].timeout = _to_int(row[10]) if len(row) > 10 else 0
        data_config.Motor_Cmd1Ind[ind] = _to_int(row[11]) if len(row) > 11 else -1
        data_config.Motor_Cmd2Ind[ind] = _to_int(row[12]) if len(row) > 12 else -1
        data_config.Motor_Cmd3Ind[ind] = _to_int(row[13]) if len(row) > 13 else -1
        data_config.Motor[ind].timeout2 = _to_int(row[14]) if len(row) > 14 else 0
        data_config.Motor[ind].typ = _to_int(row[15]) if len(row) > 15 else -1
        data_config.Motor[ind].timeoutbtn = _to_int(row[16]) if len(row) > 16 else 0
        # opzionali TR2 / Starting (>= 17,18)
        if len(row) >= 18:
            data_config.Motor_TR2Ind[ind] = _to_int(row[17])
            if len(row) >= 19:
                data_config.Motor_StartingInd[ind] = _to_int(row[18])

        # Recycling type → aggiorna indice
        try:
            if data_config.Motor[ind].typ == getattr(data_config, "MOTOR_TYPE_RECYCLING"):
                data_config.DATA_STATUS.RecyclingMotorInd = ind
        except Exception:
            pass
    logging.debug('OUT: _deserialize_obj_mot')


def _deserialize_obj_alarm(data: Dict[str, Any]) -> None:
    logger.debug('IN: _deserialize_obj_alarm')
    rows = _as_list(data.get("obj", {}).get("alarm"))
    # init Stop e warning map a inizio
    data_config.Stop_Num = 0
    for i in range(getattr(data_config, "MAX_STOP", 0) + 1):
        data_config.Stop_Ind[i] = -1
        data_config.Stop_Name[i] = ""
    try:
        for i in range(getattr(data_config, "MAX_WARNING", 0) + 1):
            data_config.DATA_ALARMS.Ind[i] = -1
    except Exception:
        pass

    for ind, row in enumerate(rows):
        if ind >= len(data_config.Alarm_Name):
            # logging.info(ind >= len(data_config.Alarm_Name), len(data_config.Alarm_Name), ind)
            logging.info(f"allarme {ind} ignorato")  # TODO: se allarmi maggiori di 192 allora versione diversa
            continue
        if not isinstance(row, (list, tuple)) or len(row) == 0:
            continue
        name = str(row[0])
        data_config.Alarm_Name[ind] = name
        data_config.Alarm_Param[ind].name = name

        # bool
        for j in range(MAX_ALARMBOOL + 1):
            val = row[1 + j] if (1 + j) < len(row) else 0
            data_config.Alarm_Param[ind].boolval[j] = _bool_from_int(val)

        # int
        for j in range(MAX_ALARMINT + 1):
            idx = 1 + (MAX_ALARMBOOL + 1) + j
            if idx < len(row):
                data_config.Alarm_Param[ind].intval[j] = _to_int(row[idx], -1)
            else:
                data_config.Alarm_Param[ind].intval[j] = -1

        # Codice allarmi
        try:
            ALARM_INT_COD = getattr(data_config, "ALARM_INT_COD")
            data_config.DATA_ALARMS.Cod[ind] = data_config.Alarm_Param[ind].intval[ALARM_INT_COD]
        except Exception:
            pass

        # Mappa warnings per safety/safetystop
        try:
            ALARM_INT_MODE = getattr(data_config, "ALARM_INT_MODE")
            ALARM_SAFETY = getattr(data_config, "ALARM_SAFETY")
            ALARM_SAFETYSTOP = getattr(data_config, "ALARM_SAFETYSTOP")
            ALARM_COD_FIRSTWARNING = getattr(data_config, "ALARM_COD_FIRSTWARNING")
            MAX_WARNING = getattr(data_config, "MAX_WARNING")
            cod = data_config.DATA_ALARMS.Cod[ind]
            mode = data_config.Alarm_Param[ind].intval[ALARM_INT_MODE]
            if mode in (ALARM_SAFETY, ALARM_SAFETYSTOP):
                if ALARM_COD_FIRSTWARNING <= cod <= ALARM_COD_FIRSTWARNING + MAX_WARNING:
                    data_config.DATA_ALARMS.Ind[cod - ALARM_COD_FIRSTWARNING] = ind
        except Exception:
            pass

        # Gestione STOP list
        try:
            ALARM_BOOL_CONFIG = getattr(data_config, "ALARM_BOOL_CONFIG")
            ALARM_STOP = getattr(data_config, "ALARM_STOP")
            ALARM_SAFETYSTOP = getattr(data_config, "ALARM_SAFETYSTOP")
            mode = data_config.Alarm_Param[ind].intval[getattr(data_config, "ALARM_INT_MODE")]
            if data_config.Alarm_Param[ind].boolval[ALARM_BOOL_CONFIG] and (mode in (ALARM_STOP, ALARM_SAFETYSTOP)):
                s = data_config.Stop_Num
                data_config.Stop_Ind[s] = ind
                data_config.Stop_Name[s] = name
                data_config.Stop_Num = s + 1
        except Exception:
            pass
    logger.debug('OUT: _deserialize_obj_alarm')


def _deserialize_obj_maint(data: Dict[str, Any]) -> None:
    logger.debug('IN: _deserialize_obj_maint')
    rows = _as_list(data.get("obj", {}).get("maint"))
    for ind, row in enumerate(rows):
        if not isinstance(row, (list, tuple)) or len(row) == 0:
            continue
        name = str(row[0])
        data_config.Maint_Name[ind] = name
        data_config.Maint_Param[ind].name = name

        for j in range(MAX_MAINTBOOL + 1):
            val = row[1 + j] if (1 + j) < len(row) else 0
            data_config.Maint_Param[ind].boolval[j] = _bool_from_int(val)

        for j in range(MAX_MAINTINT + 1):
            idx = 1 + (MAX_MAINTBOOL + 1) + j
            if idx < len(row):
                data_config.Maint_Param[ind].intval[j] = _to_int(row[idx])
        # Codice manutenzione (se presente struttura DATA_MAINT)
        try:
            MAINT_INT_COD = getattr(data_config, "MAINT_INT_COD")
            data_config.DATA_MAINT.Cod[ind] = data_config.Maint_Param[ind].intval[MAINT_INT_COD]
        except Exception:
            pass
    logger.debug('OUT: _deserialize_obj_maint')

def _deserialize_obj_toolset(data: Dict[str, Any]) -> None:
    logger.debug('IN: _deserialize_obj_toolset')
    rows = _as_list(data.get("obj", {}).get("toolset"))
    for ind, row in enumerate(rows):
        if not isinstance(row, (list, tuple)) or len(row) == 0:
            continue
        # Struttura: [Name, bools..., ints..., reals..., outputs(int..,dint..)*]
        name = str(row[0])
        data_config.Toolset_Name[ind] = name
        data_config.Toolset_Param[ind].name = name

        # bool
        off = 1
        for j in range(MAX_TOOLSETBOOL + 1):
            val = row[off + j] if off + j < len(row) else 0
            data_config.Toolset_Param[ind].boolval[j] = _bool_from_int(val)
        off += (MAX_TOOLSETBOOL + 1)

        # int
        for j in range(MAX_TOOLSETINT + 1):
            val = row[off + j] if off + j < len(row) else 0
            data_config.Toolset_Param[ind].intval[j] = _to_int(val)
        off += (MAX_TOOLSETINT + 1)

        # real (+ typval,fc,offset tutti MISURA_LUNGH)
        for j in range(MAX_TOOLSETREAL + 1):
            val = row[off + j] if off + j < len(row) else 0.0
            fv = _to_float(val)
            data_config.Toolset_Param[ind].realvalcfg[j] = fv
            data_config.Toolset_Param[ind].realval[j] = fv
            try:
                MISURA_LUNGH = getattr(data_config, "MISURA_LUNGH")
                data_config.Toolset_Param[ind].typval[j] = MISURA_LUNGH
                data_config.Toolset_Param[ind].fcval[j] = data_config.UM_FC[MISURA_LUNGH]
                data_config.Toolset_Param[ind].offsetval[j] = data_config.UM_Offset[MISURA_LUNGH]
            except Exception:
                pass
        off += (MAX_TOOLSETREAL + 1)

        # output matrix
        block_len = (MAX_TOOLSETOUTPUTINT + 1) + (MAX_TOOLSETOUTPUTDINT + 1)
        for i_out in range(MAX_TOOLSETOUTPUT + 1):
            # int
            for j in range(MAX_TOOLSETOUTPUTINT + 1):
                idx = off + j + i_out * block_len
                val = row[idx] if idx < len(row) else 0
                data_config.Toolset_Param[ind].output[i_out].intval[j] = _to_int(val)
            # dint
            base = off + (MAX_TOOLSETOUTPUTINT + 1) + i_out * block_len
            for j in range(MAX_TOOLSETOUTPUTDINT + 1):
                idx = base + j
                val = row[idx] if idx < len(row) else 0
                data_config.Toolset_Param[ind].output[i_out].dintval[j] = _to_int(val)
    logger.debug('OUT: _deserialize_obj_toolset')


# ------------------ Finalize ------------------
def _check_config_version(data: dict) -> tuple[int, int, int, int]:
    """
    Deduce la versione del file di configurazione basandosi
    sulle dimensioni di sezioni chiave (alarm, param, in...).
    Restituisce (PLCVersion1, PLCVersion2, PLCVersion3, PLCVersion4).
    """
    v1 = v2 = v3 = v4 = 0

    # --- estrazione sicura dei blocchi ---
    obj = data.get("obj", {})
    alarms = _as_list(obj.get("alarm"))
    stato_bool = _as_list(data.get("in"))

    # --- gestione 'param' compatibile con lista o dict ---
    raw_param = data.get("param", {})
    params = {}
    if isinstance(raw_param, list):
        for entry in raw_param:
            if isinstance(entry, dict):
                params.update(entry)
    elif isinstance(raw_param, dict):
        params = raw_param

    pbool = _as_list(params.get("pbool"))
    pint = _as_list(params.get("pint"))

    # --- calcoli lunghezze ---
    len_alarms = len(alarms)
    len_pbool = len(pbool)
    len_pint = len(pint)
    len_stato = len(stato_bool)

    # --- logica di deduzione versione ---
    if len_alarms == 223:
        v2 = 25
    elif len_alarms == 191:
        v2 = 24

    if len_pbool == 71:
        v2, v3, v4 = 25, 42, 1
    elif len_pbool == 63:
        v2, v3 = 25, 28

    if len_stato == 151:
        v2, v3, v4 = 25, 42, 1
    elif len_stato == 135:
        v2, v3 = 25, 42
    elif len_stato == 127:
        v2 = 18

    if len_pint == 72:
        v2 = 18
    # fallback nel caso non riconosca nulla
    if v2 == 0:
        v2 = 25 if len_alarms > 0 else 0

    return v1, v2, v3, v4


def _finalize_config(data: Dict[str, Any]) -> None:
    """ Allineamenti finali a EOF """
    data_config.Config_Header[HEADER_SN] = data_config.ParamInt[INT_SN]
    data_config.Config_Header[HEADER_TYPEVERSION] = data_config.CFGVersion
    data_config.PLCVersion1, data_config.PLCVersion2, data_config.PLCVersion3, data_config.PLCVersion4 = _check_config_version(data)
    data_config.CFGVersion = data_config.PLCVersion1 * 100 + data_config.PLCVersion2
    # logging.info(f"*CFG v{data_config.PLCVersion1}.{data_config.PLCVersion2}.{data_config.PLCVersion3}.{data_config.PLCVersion4}")
    # essendo script based non c è modo di reperirlo dal config


# ------------------- Logic --------------------
def get_io_index(iotype: int, idx: Optional[int] = None) -> List[int] | int | None:
    """
    Restituisce gli indici globali degli IO in base al tipo richiesto.
    - Se idx è None → lista completa degli indici globali di quel tipo.
    - Se idx è un int → ritorna il singolo indice globale corrispondente all'indice locale del tipo.
    """
    # Mappa iotype → (start, max_count)
    if iotype == IO_DI:
        start = 0
        count = MAX_DI + 1
    elif iotype == IO_AI:
        start = MAX_DI + 1
        count = MAX_AI + 1
    elif iotype == IO_DO:
        start = (MAX_DI + 1) + (MAX_AI + 1)
        count = MAX_DO + 1
    elif iotype == IO_AO:
        start = (MAX_DI + 1) + (MAX_AI + 1) + (MAX_DO + 1)
        count = MAX_AO + 1
    elif iotype == IO_RI:
        start = (MAX_DI + 1) + (MAX_AI + 1) + (MAX_DO + 1) + (MAX_AO + 1)
        count = MAX_RI + 1
    else:
        raise ValueError(f"Tipo IO non riconosciuto: {iotype}")

    if idx is None:
        # Lista completa di tutti gli indici globali per quel tipo
        return list(range(start, start + count))
    else:
        # Singolo indice globale, se è nel range
        if 0 <= idx < count:
            return start + idx
        return None


def get_io_name(iotype: int, Ind: int) -> Optional[str]:
    """
    Ritorna il nome (string) dell'IO dato iotype e indice *locale* (Ind).
    Se out of range o non definito, ritorna None.
    """
    is_system = decode_sys_addr_name(Ind)
    if is_system and iotype == IO_DI:
        return is_system
    # calcolo start e count per blocco
    if iotype == IO_DI:
        start = 0
        count = MAX_DI + 1
    elif iotype == IO_AI:
        start = (MAX_DI + 1)
        count = MAX_AI + 1
    elif iotype == IO_DO:
        start = (MAX_DI + 1) + (MAX_AI + 1)
        count = MAX_DO + 1
    elif iotype == IO_AO:
        start = (MAX_DI + 1) + (MAX_AI + 1) + (MAX_DO + 1)
        count = MAX_AO + 1
    elif iotype == IO_RI:
        start = (MAX_DI + 1) + (MAX_AI + 1) + (MAX_DO + 1) + (MAX_AO + 1)
        count = MAX_RI + 1
    else:
        return None  # tipo sconosciuto

    # bounds check indice locale
    if Ind < 0 or Ind >= count:
        return None

    k = start + Ind  # indice globale nell’array IO_Name

    # doppio fallback: IO_Name -> IO_Param[k].name -> None
    try:
        name = data_config.IO_Name[k]
        if name == 'None' or name is None:
            name = '-'
        if name:
            return name
    except Exception:
        pass

    try:
        nm = getattr(data_config.IO_Param[k], "name", "")
        return nm if nm else None
    except Exception:
        return None

def get_io_fullname(iotype: int, Ind: int):
    return f'[{Ind}] {get_io_name(iotype, Ind)}'

def get_axis_name(Ind: int):
    return data_config.Axis_Name[Ind]


def get_axis_fullname(Ind: int):
    name = get_axis_name(Ind)
    return f'[{Ind}] {name}'


def _debug_intval(iotype: int = None):
    AxisParamIntVals = data_config.Axis_Param[0].intval
    for idx, val in enumerate(AxisParamIntVals):
        idx_name = Type_AxisParam_Map["_intval"][idx]
        display = Type_AxisParam_Map["intval"][idx_name]["display"]
        origin = Type_AxisParam_Map["intval"][idx_name]["origin"]
        _type = Type_AxisParam_Map["intval"][idx_name].get("type", None)
        if iotype is not None:
            if _type:
                if iotype not in _type:
                    continue
            else:
                continue
        axis_name = get_axis_name(Ind=0)
        try:
            origin = Type_AxisParam_Map["intval"][idx_name]["origin"].format(0, axis_name)
        except:
            pass
        logging.info(f'{idx}\t{display}\t-\tx{val}\t-\t{origin}')


def _debug_realval(iotype: int = None):
    AxisParamRealVals = data_config.Axis_Param[0].realval
    for idx, val in enumerate(AxisParamRealVals):
        idx_name = Type_AxisParam_Map["_realval"][idx]
        display = Type_AxisParam_Map["realval"][idx_name]["display"]
        origin = Type_AxisParam_Map["realval"][idx_name]["origin"]
        _type = Type_AxisParam_Map["realval"][idx_name].get("type", None)
        if iotype is not None:
            if _type:
                if iotype not in _type:
                    continue
            else:
                continue
        axis_name = get_axis_name(Ind=0)
        try:
            origin = Type_AxisParam_Map["realval"][idx_name]["origin"].format(0, axis_name)
        except:
            pass
        logging.info(f'{idx}\t{display}\t-\tx{val}\t-\t{origin}')


def _debug_boolval(iotype: int = None):
    AxisParamBoolVals = data_config.Axis_Param[0].boolval
    for idx, val in enumerate(AxisParamBoolVals):
        idx_name = Type_AxisParam_Map["_boolval"][idx]
        display = Type_AxisParam_Map["boolval"][idx_name]["display"]
        origin = Type_AxisParam_Map["boolval"][idx_name]["origin"]
        _type = Type_AxisParam_Map["boolval"][idx_name].get("type", None)
        if iotype is not None:
            if _type:
                if iotype not in _type:
                    continue
            else:
                continue
        axis_name = get_axis_name(Ind=0)
        try:
            origin = Type_AxisParam_Map["boolval"][idx_name]["origin"].format(0, axis_name)
        except:
            pass
        logging.info(f'{idx}\t{display}\t-\tx{val}\t-\t{origin}')


def _debug_ioparam(iotype: int, Ind: int = 0):
    if iotype == IO_DI:
        logging.info(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_DI_List[Ind]}')
    elif iotype == IO_DO:
        logging.info(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_DO_List[Ind]}')
    elif iotype == IO_AI:
        logging.info(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_AI_List[Ind]}')
    elif iotype == IO_AO:
        logging.info(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_AO_List[Ind]}')
    elif iotype == IO_RI:
        logging.info(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_RI_List[Ind]}')


def run_params_scan(iotype: int, ind_target: int, verbose: bool = False) -> List[str]:
    logger.debug('IN: run_params_scan')
    _return = []
    if iotype == IO_DI:
        for pid, val in enumerate(data_config.InInd):
            if val == ind_target:
                if pid < len(Config_Map["InInd"]):
                    entry = Config_Map["_InInd"][pid]
                    txt = f'{Config_Map["InInd"][entry]["origin"]}\t→\t{Config_Map["InInd"][entry]["display"]}'
                    _return.append(txt)
                    if verbose:
                        logging.info(txt)

        for idx, val in enumerate(data_config.ParamInt):
            if idx not in Config_Map["_ParamInt"]:
                # logging.warning(f'ParamInt out of range idx: {idx}')
                continue  # evita KeyError se indice non mappato
            idx_name = Config_Map["_ParamInt"][idx]
            ParamInt_Type = Config_Map["ParamInt"][idx_name].get("type", [])
            if iotype in ParamInt_Type:
                if val == ind_target:
                    idx_name = Config_Map["_ParamInt"][idx]
                    display = Config_Map["ParamInt"][idx_name]["display"]
                    origin = Config_Map["ParamInt"][idx_name]["origin"]
                    io_name = get_io_name(iotype=IO_DI, Ind=ind_target)
                    txt = f'{origin}\t→\t{display}'
                    _return.append(txt)
                    if verbose:
                        logging.info(txt)
    elif iotype == IO_DO:
        for pid, val in enumerate(data_config.OutInd):
            if val == ind_target:
                if pid < len(Config_Map["OutInd"]):
                    entry = Config_Map["_OutInd"][pid]
                    txt = f'{Config_Map["OutInd"][entry]["origin"]}\t→\t{Config_Map["OutInd"][entry]["display"]}'
                    _return.append(txt)
                    if verbose:
                        logging.info(txt)

        for idx, val in enumerate(data_config.ParamInt):
            if idx not in Config_Map["_ParamInt"]:
                # logging.warning(f'ParamInt out of range idx: {idx}')
                continue  # evita KeyError se indice non mappato
            idx_name = Config_Map["_ParamInt"][idx]
            ParamInt_Type = Config_Map["ParamInt"][idx_name].get("type", [])
            if iotype in ParamInt_Type:
                if val == ind_target:
                    idx_name = Config_Map["_ParamInt"][idx]
                    display = Config_Map["ParamInt"][idx_name]["display"]
                    origin = Config_Map["ParamInt"][idx_name]["origin"]
                    io_name = get_io_name(iotype=IO_DI, Ind=ind_target)
                    txt = f'{origin}\t→\t{display}'
                    _return.append(txt)
                    if verbose:
                        logging.info(txt)
    elif iotype == IO_AI:
        for idx, val in enumerate(data_config.ParamInt):
            if idx not in Config_Map["_ParamInt"]:
                # logging.warning(f'ParamInt out of range idx: {idx}')
                continue  # evita KeyError se indice non mappato
            idx_name = Config_Map["_ParamInt"][idx]
            ParamInt_Type = Config_Map["ParamInt"][idx_name].get("type", [])
            if iotype in ParamInt_Type:
                if val == ind_target:
                    idx_name = Config_Map["_ParamInt"][idx]
                    display = Config_Map["ParamInt"][idx_name]["display"]
                    origin = Config_Map["ParamInt"][idx_name]["origin"]
                    io_name = get_io_name(iotype=IO_DI, Ind=ind_target)
                    txt = f'{origin}\t→\t{display}'
                    _return.append(txt)
                    if verbose:
                        logging.info(txt)
    return _return


def run_axis_scan(iotype: int, ind_target: int = None, axisInd: int = None, verbose: bool = False) -> List[str]:
    if axisInd is None:
        logging.debug('IN: run_axis_scan')
    """
    iotype: tipo di io
    Ind: indice da cercare
    axisInd: asse dove cercarlo
    """
    if axisInd is not None:
        _return = []
        if iotype == IO_DI:
            AxisParamIntVals = data_config.Axis_Param[axisInd].intval
            for idx, val in enumerate(AxisParamIntVals):
                idx_name = Type_AxisParam_Map["_intval"][idx]
                axis_Type = Type_AxisParam_Map["intval"][idx_name].get("type", [])
                if iotype in axis_Type:
                    if val == ind_target:
                        display = Type_AxisParam_Map["intval"][idx_name]["display"]
                        origin = Type_AxisParam_Map["intval"][idx_name]["origin"]
                        axis_name = get_axis_name(Ind=axisInd)
                        txt = f"{origin.format(axisInd, axis_name)}\t→\t{display}"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
        if iotype == IO_RI:
            AxisParamIntVals = data_config.Axis_Param[axisInd].intval
            for idx, val in enumerate(AxisParamIntVals):
                idx_name = Type_AxisParam_Map["_intval"][idx]
                axis_Type = Type_AxisParam_Map["intval"][idx_name].get("type", [])
                if iotype in axis_Type:
                    if val == ind_target:
                        display = Type_AxisParam_Map["intval"][idx_name]["display"]
                        origin = Type_AxisParam_Map["intval"][idx_name]["origin"]
                        axis_name = get_axis_name(Ind=axisInd)
                        txt = f"{origin.format(axisInd, axis_name)}\t→\t{display}"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
        return _return
    else:
        _return = []
        for i in range(0, MAX_ASSE):
            found = run_axis_scan(iotype=iotype, ind_target=ind_target, axisInd=i, verbose=verbose)
            if found:
                _return.extend(found)
    if axisInd is None:
        logging.debug('OUT: run_axis_scan')
    return _return


def run_input_scan(iotype: int, ind_target: int = None, inputInd: int = None, verbose: bool = False) -> List[str]:
    if inputInd is None:
        logging.debug('IN: run_input_scan')
    """
    iotype: tipo di io
    Ind: indice da cercare
    InputInd: input dove cercarlo
    """
    if inputInd is not None:
        _return = []
        if iotype == IO_DI:
            InputParamIntVals = data_config.Input_Param[inputInd].intval
            for idx, val in enumerate(InputParamIntVals):
                idx_name = Type_InputParam_Map["_intval"][idx]
                input_Type = Type_InputParam_Map["intval"][idx_name].get("type", [])
                if iotype in input_Type:
                    if val == ind_target:
                        display = Type_InputParam_Map["intval"][idx_name]["display"]
                        origin = Type_InputParam_Map["intval"][idx_name]["origin"]
                        txt = f"{origin.format(inputInd)}\t→\t{display}"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
        if iotype == IO_AI:
            InputParamIntVals = data_config.Input_Param[inputInd].intval
            for idx, val in enumerate(InputParamIntVals):
                idx_name = Type_InputParam_Map["_intval"][idx]
                input_Type = Type_InputParam_Map["intval"][idx_name].get("type", [])
                if iotype in input_Type:
                    if val == ind_target:
                        display = Type_InputParam_Map["intval"][idx_name]["display"]
                        origin = Type_InputParam_Map["intval"][idx_name]["origin"]
                        txt = f"{origin.format(inputInd)}\t→\t{display}"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
        return _return
    else:
        _return = []
        for i in range(0, MAX_INPUT):
            found = run_input_scan(iotype=iotype, ind_target=ind_target, inputInd=i, verbose=verbose)
            if found:
                _return.extend(found)
    if inputInd is None:
        logging.debug('OUT: run_input_scan')
    return _return


def run_output_scan(iotype: int, ind_target: int = None, outputInd: int = None, verbose: bool = False) -> List[str]:
    if outputInd is None:
        logging.debug('IN: run_output_scan')
    """
    iotype: tipo di io
    Ind: indice da cercare
    outputInd: output dove cercarlo
    """
    if outputInd is not None:
        _return = []
        if iotype == IO_DI:
            OutputParamIntVals = data_config.Output_Param[outputInd].intval
            custom_params = {
                "OUTPUT_INT_ACTIND": "ACT",
                "OUTPUT_INT_ENAB": "ENAB",
                "OUTPUT_INT_ENAB2": "ENAB2",
                "OUTPUT_INT_ENAB3": "ENAB3",
            }
            for idx_name, display in custom_params.items():
                idx = next((k for k, v in Type_OutputParam_Map["_intval"].items() if v == idx_name), None)
                if idx is not None:
                    if OutputParamIntVals[idx] == ind_target:
                        origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                        txt = f"{origin.format(outputInd)}\t→\t{display}"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
                else:
                    logging.warning(f'{idx_name} non definito')
            if OutputParamIntVals[OUTPUT_INT_TIPO] == OUTPUT_ATV340:
                custom_params = {
                    "OUTPUT_INT_DIG1IND": "DIG1 ATV340 TORQUE",
                    "OUTPUT_INT_DIG2IND": "DIG2 ATV340 ALARM",
                    "OUTPUT_INT_CCIND": "CC ATV340 THERMALFAN",
                }
                for idx_name, display in custom_params.items():
                    idx = next((k for k, v in Type_OutputParam_Map["_intval"].items() if v == idx_name), None)
                    if idx is not None:
                        if OutputParamIntVals[idx] == ind_target:
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            txt = f"{origin.format(outputInd)}\t→\t{display}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
                    else:
                        logging.warning(f'{idx_name} non definito')
        elif iotype == IO_DO:
            OutputParamIntVals = data_config.Output_Param[outputInd].intval
            if OutputParamIntVals[OUTPUT_INT_TIPO] not in [OUTPUT_ADV, OUTPUT_PSLCAN, OUTPUT_ATV340]:
                for idx, val in enumerate(OutputParamIntVals):
                    idx_name = Type_OutputParam_Map["_intval"][idx]
                    output_Type = Type_OutputParam_Map["intval"][idx_name].get("type", [])
                    if iotype in output_Type:
                        if val == ind_target:
                            display = Type_OutputParam_Map["intval"][idx_name]["display"]
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            txt = f"{origin.format(outputInd)}\t→\t{display}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
            elif OutputParamIntVals[OUTPUT_INT_TIPO] == OUTPUT_ADV:
                custom_params = {
                    "OUTPUT_INT_ANA2IND": "ADV START",
                    "OUTPUT_INT_DIG1IND": "ADV ENABLE",
                    "OUTPUT_INT_DIG2IND": "ADV BRAKE",
                    "OUTPUT_INT_CCIND": "CC",
                }
                for idx_name, display in custom_params.items():
                    idx = next((k for k, v in Type_OutputParam_Map["_intval"].items() if v == idx_name),
                               None)
                    if idx is not None:
                        if OutputParamIntVals[idx] == ind_target:
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            txt = f"{origin.format(outputInd)}\t→\t{display}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
                    else:
                        logging.warning(f'{idx_name} non definito')
            elif OutputParamIntVals[OUTPUT_INT_TIPO] == OUTPUT_PSLCAN:
                custom_params = {
                    "OUTPUT_INT_DIG1IND": "ADV ENABLE",
                    "OUTPUT_INT_DIG2IND": "ADV BRAKE",
                    "OUTPUT_INT_CCIND": "CC",
                }
                for idx_name, display in custom_params.items():
                    idx = next((k for k, v in Type_OutputParam_Map["_intval"].items() if v == idx_name),
                               None)
                    if idx is not None:
                        if OutputParamIntVals[idx] == ind_target:
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            txt = f"{origin.format(outputInd)}\t→\t{display}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
                    else:
                        logging.warning(f'{idx_name} non definito')
            elif OutputParamIntVals[OUTPUT_INT_TIPO] == OUTPUT_ATV340:
                custom_params = {
                    "OUTPUT_INT_ANA2IND": "ANA2 ATV340 START FAN",
                }
                for idx_name, display in custom_params.items():
                    idx = next((k for k, v in Type_OutputParam_Map["_intval"].items() if v == idx_name), None)
                    if idx is not None:
                        if OutputParamIntVals[idx] == ind_target:
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            txt = f"{origin.format(outputInd)}\t→\t{display}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
                    else:
                        logging.warning(f'{idx_name} non definito')
            if OutputParamIntVals[OUTPUT_INT_TIPO] == OUTPUT_SELSLOW:
                custom_params = {
                    "OUTPUT_INT_ANA1IND": "DIG1ADD",
                    "OUTPUT_INT_ANA2IND": "DIG2ADD",
                }
                for idx_name, display in custom_params.items():
                    idx = next((k for k, v in Type_OutputParam_Map["_intval"].items() if v == idx_name), None)
                    if idx is not None:
                        if OutputParamIntVals[idx] == ind_target:
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            txt = f"{origin.format(outputInd)}\t→\t{display}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
                    else:
                        logging.warning(f'{idx_name} non definito')
        elif iotype == IO_AI:
            OutputParamIntVals = data_config.Output_Param[outputInd].intval
            if OutputParamIntVals[OUTPUT_INT_TIPO] not in [OUTPUT_ADV, OUTPUT_PSLCAN]:
                for idx, val in enumerate(OutputParamIntVals):
                    idx_name = Type_OutputParam_Map["_intval"][idx]
                    output_Type = Type_OutputParam_Map["intval"][idx_name].get("type", [])
                    if iotype in output_Type:
                        if val == ind_target:
                            display = Type_OutputParam_Map["intval"][idx_name]["display"]
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            if verbose:
                                logging.info(f"{origin.format(outputInd)}\t→\t{display}")
            if OutputParamIntVals[OUTPUT_INT_TIPO] == OUTPUT_PSLCAN:
                custom_params = {
                    "OUTPUT_INT_ADDPARAM2": "STATUS1 PSLCAN",
                    "OUTPUT_INT_ADDPARAM4": "STATUS2 PSLCAN",
                }
                for idx_name, display in custom_params.items():
                    idx = next((k for k, v in Type_OutputParam_Map["_intval"].items() if v == idx_name), None)
                    if idx is not None:
                        if OutputParamIntVals[idx] == ind_target:
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            txt = f"{origin.format(outputInd)}\t→\t{display}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
                    else:
                        logging.warning(f'{idx_name} non definito')
        elif iotype == IO_AO:
            OutputParamIntVals = data_config.Output_Param[outputInd].intval
            if OutputParamIntVals[OUTPUT_INT_TIPO] not in [OUTPUT_ADV, OUTPUT_PSLCAN]:
                for idx, val in enumerate(OutputParamIntVals):
                    idx_name = Type_OutputParam_Map["_intval"][idx]
                    output_Type = Type_OutputParam_Map["intval"][idx_name].get("type", [])
                    if iotype in output_Type:
                        if val == ind_target:
                            display = Type_OutputParam_Map["intval"][idx_name]["display"]
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            if verbose:
                                logging.info(f"{origin.format(outputInd)}\t→\t{display}")
            if OutputParamIntVals[OUTPUT_INT_TIPO] == OUTPUT_PSLCAN:
                custom_params = {
                    "OUTPUT_INT_ANA1IND": "ANA1",
                    "OUTPUT_INT_ANA2IND": "ANA2",
                    "OUTPUT_INT_ADDPARAM1": "CTRL1 PSLCAN",
                    "OUTPUT_INT_ADDPARAM3": "CTRL2 PSLCAN",
                }
                for idx_name, display in custom_params.items():
                    idx = next((k for k, v in Type_OutputParam_Map["_intval"].items() if v == idx_name), None)
                    if idx is not None:
                        if OutputParamIntVals[idx] == ind_target:
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            txt = f"{origin.format(outputInd)}\t→\t{display}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
                    else:
                        logging.warning(f'{idx_name} non definito')

    else:
        _return = []
        for i in range(0, MAX_OUTPUT):
            found = run_output_scan(iotype=iotype, ind_target=ind_target, outputInd=i, verbose=verbose)
            if found:
                _return.extend(found)
    if outputInd is None:
        logging.debug('OUT: run_output_scan')
    return _return


def run_feedback_scan(iotype: int, ind_target: int = None, feedbackInd: int = None, verbose: bool = False) -> List[str]:
    if feedbackInd is None:
        logging.debug('IN: run_feedback_scan')
    """
    iotype: tipo di io
    Ind: indice da cercare
    feedbackInd: output dove cercarlo
    """
    if feedbackInd is not None:
        _return = []
        if iotype == IO_DI:
            FeedbackParamIntVals = data_config.Feedback_Param[feedbackInd].intval
            if FeedbackParamIntVals[FB_INT_RESETIND] == ind_target:
                origin = Type_FeedbackParam_Map["intval"]["FB_INT_RESETIND"]["origin"]
                display = Type_FeedbackParam_Map["intval"]["FB_INT_RESETIND"]["display"]
                txt = f"{origin.format(feedbackInd)}\t→\t{display}"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if FeedbackParamIntVals[FB_INT_TIPO] == FB_DI:
                if FeedbackParamIntVals[FB_INT_ININD] == ind_target:
                    origin = Type_FeedbackParam_Map["intval"]["FB_INT_ININD"]["origin"]
                    display = Type_FeedbackParam_Map["intval"]["FB_INT_ININD"]["display"]
                    txt = f"{origin.format(feedbackInd)}\t→\t{display}"
                    _return.append(txt)
                    if verbose:
                        logging.info(txt)
        elif iotype == IO_AI:
            FeedbackParamIntVals = data_config.Feedback_Param[feedbackInd].intval
            if FeedbackParamIntVals[FB_INT_TIPO] in [FB_AI, FB_AHSC,
                                                     FB_AI2]:  # TODO: quello a ritenzione di analogico come si chiama?
                if FeedbackParamIntVals[FB_INT_ININD] == ind_target:
                    origin = Type_FeedbackParam_Map["intval"]["FB_INT_ININD"]["origin"]
                    display = Type_FeedbackParam_Map["intval"]["FB_INT_ININD"]["display"]
                    txt = f"{origin.format(feedbackInd)}\t→\t{display}"
                    _return.append(txt)
                    if verbose:
                        logging.info(txt)
    else:
        _return = []
        for i in range(0, MAX_FEEDBACK):
            found = run_feedback_scan(iotype=iotype, ind_target=ind_target, feedbackInd=i, verbose=verbose)
            if found:
                _return.extend(found)
    if feedbackInd is None:
        logging.debug('OUT: run_feedback_scan')
    return _return


def run_io_expr_scan(iotype: int, ind_target: int = None, verbose: bool = False) -> List[str]:
    logger.debug('IN: run_io_expr_scan')
    _return = []
    if iotype == IO_DI:
        for Ind in range(0, len(data_config.IO_DI_List)):
            if data_config.IO_DI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
                if len(data_config.IO_DI_List[Ind].exprintval) <= 1:
                    continue
                expr_type = data_config.IO_DI_List[Ind].exprintval[0]
                # 🔁 Ciclo sui gruppi (partendo da index 1, passo di 3)
                for i in range(1, len(data_config.IO_DI_List[Ind].exprintval), 3):
                    if i + 2 >= len(data_config.IO_DI_List[Ind].exprintval):
                        # if DEBUG_DEBUG_DEBUG:
                        #     logging.info('xERR_001')
                        continue
                    not_val, opnd_val, oper_val = data_config.IO_DI_List[Ind].exprintval[i:i + 3]
                    try:
                        _ = [IO_EXPR_NONE, IO_EXPR_VAL, IO_EXPR_NOTVAL]
                    except NameError:
                        logging.debug('Costanti IO_EXPR_NONE, IO_EXPR_VAL, IO_EXPR_NOTVAL non definite in questa versione!') # TODO: gestire meglio
                        continue
                    if not_val in [IO_EXPR_NONE, IO_EXPR_VAL, IO_EXPR_NOTVAL]:
                        group_num = ((i - 1) // 3)  # + 1
                        if opnd_val == ind_target:
                            txt = f"IO\t→\tDI\t→\t[{Ind}] {get_io_name(iotype=IO_DI, Ind=Ind)}\t→\tExpr\t→\tN{group_num}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
    elif iotype == IO_AI:
        # EXPR DI
        for Ind in range(0, len(data_config.IO_DI_List)):
            if data_config.IO_DI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
                if len(data_config.IO_DI_List[Ind].exprintval) <= 1:
                    continue
                expr_type = data_config.IO_DI_List[Ind].exprintval[0]
                # 🔁 Ciclo sui gruppi (partendo da index 1, passo di 3)
                for i in range(1, len(data_config.IO_DI_List[Ind].exprintval), 3):
                    if i + 2 >= len(data_config.IO_DI_List[Ind].exprintval):
                        # if DEBUG_DEBUG_DEBUG:
                        #     logging.info('xERR_001')
                        continue
                    not_val, opnd_val, oper_val = data_config.IO_DI_List[Ind].exprintval[i:i + 3]
                    if not_val in [IO_EXPR_AIEQ0, IO_EXPR_AINE0, IO_EXPR_AIGT0,
                                   IO_EXPR_AIGE0, IO_EXPR_AILT0, IO_EXPR_AILE0]:
                        group_num = ((i - 1) // 3)  # + 1
                        if opnd_val == ind_target:
                            txt = f"IO\t→\tDI\t→\t[{Ind}] {get_io_name(iotype=IO_DI, Ind=Ind)}\t→\tExpr\t→\tN{group_num}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
        # EXPR RI
        for Ind in range(0, len(data_config.IO_RI_List)):
            if data_config.IO_RI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
                if len(data_config.IO_RI_List[Ind].exprintval) <= 1:
                    continue
                expr_type = data_config.IO_RI_List[Ind].exprintval[0]
                # 🔁 Ciclo sui gruppi (partendo da index 1, passo di 3)
                for i in range(1, len(data_config.IO_RI_List[Ind].exprintval), 3):
                    if i + 2 >= len(data_config.IO_RI_List[Ind].exprintval):
                        # if DEBUG_DEBUG_DEBUG:
                        #     logging.info('xERR_001')
                        continue
                    not_val, opnd_val, oper_val = data_config.IO_RI_List[Ind].exprintval[i:i + 3]
                    if not_val in [IO_EXPR_AI, IO_EXPR_ABSAI]:
                        group_num = ((i - 1) // 3)  # + 1
                        if opnd_val == ind_target:
                            txt = f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tExpr\t→\tN{group_num}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
    elif iotype == IO_RI:
        # EXPR DI
        for Ind in range(0, len(data_config.IO_DI_List)):
            if data_config.IO_DI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
                if len(data_config.IO_DI_List[Ind].exprintval) <= 1:
                    continue
                expr_type = data_config.IO_DI_List[Ind].exprintval[0]
                # 🔁 Ciclo sui gruppi (partendo da index 1, passo di 3)
                for i in range(1, len(data_config.IO_DI_List[Ind].exprintval), 3):
                    if i + 2 >= len(data_config.IO_DI_List[Ind].exprintval):
                        # if DEBUG_DEBUG_DEBUG:
                        #     logging.info('xERR_001')
                        continue
                    not_val, opnd_val, oper_val = data_config.IO_DI_List[Ind].exprintval[i:i + 3]
                    if not_val in [IO_EXPR_RIEQ0, IO_EXPR_RINE0, IO_EXPR_RIGT0,
                                   IO_EXPR_RIGE0, IO_EXPR_RILT0, IO_EXPR_RILE0]:
                        group_num = ((i - 1) // 3)  # + 1
                        if opnd_val == ind_target:
                            txt = f"IO\t→\tDI\t→\t[{Ind}] {get_io_name(iotype=IO_DI, Ind=Ind)}\t→\tExpr\t→\tN{group_num}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
        # EXPR RI
        for Ind in range(0, len(data_config.IO_RI_List)):
            if data_config.IO_RI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
                if len(data_config.IO_RI_List[Ind].exprintval) <= 1:
                    continue
                expr_type = data_config.IO_RI_List[Ind].exprintval[0]
                # 🔁 Ciclo sui gruppi (partendo da index 1, passo di 3)
                for i in range(1, len(data_config.IO_RI_List[Ind].exprintval), 3):
                    if i + 2 >= len(data_config.IO_RI_List[Ind].exprintval):
                        # if DEBUG_DEBUG_DEBUG:
                        #     logging.info('xERR_001')
                        continue
                    not_val, opnd_val, oper_val = data_config.IO_RI_List[Ind].exprintval[i:i + 3]
                    if not_val in [IO_EXPR_RI, IO_EXPR_ABSRI]:
                        group_num = ((i - 1) // 3)  # + 1
                        if opnd_val == ind_target:
                            txt = f"IO\t→\tRI [{Ind}]\t→\t{get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tExpr\t→\tN{group_num}"
                            _return.append(txt)
                            if verbose:
                                logging.info(txt)
    logger.debug('OUT: run_io_expr_scan')
    return _return


def run_io_scan(iotype: int, ind_target: int = None, verbose: bool = False) -> List[str]:
    logging.debug('IN: run_io_scan')
    _return = []
    if iotype == IO_DI:
        for Ind in range(0, len(data_config.IO_DI_List)):
            if data_config.IO_DI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
                if data_config.IO_DI_List[Ind].intval[IO_INT_TIMEOUT] == -1:
                    continue  # il campo non è visibile
                # campo In del DI
                delay_di = data_config.IO_DI_List[Ind].intval[IO_INT_ININD]
                if delay_di and delay_di == ind_target:
                    txt = f"IO\t→\tDI\t→\t[{Ind}] {get_io_name(iotype=IO_DI, Ind=Ind)}\t→\tIn"
                    _return.append(txt)
                    if verbose:
                        logging.info(txt)
        found = run_io_expr_scan(iotype=IO_DI, ind_target=ind_target, verbose=verbose)
        if found:
            _return.extend(found)

        # campo In del DO
        for Ind in range(0, len(data_config.IO_DO_List)):
            if data_config.IO_DO_List[Ind].intval[IO_INT_ININD] == ind_target:
                txt = f"IO\t→\tDO\t→\t[{Ind}] {get_io_name(iotype=IO_DO, Ind=Ind)}\t→\tIn"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
        for Ind in range(0, len(data_config.IO_RI_List)):
            if data_config.IO_RI_List[Ind].intval[IO_INT_ADDRTYPE] in [IO_TYPE_FUNC_TOT, IO_TYPE_FUNC_TOTAUTO,
                                                                       IO_TYPE_FUNC_TOTMAN, IO_TYPE_FUNC_DTOT,
                                                                       IO_TYPE_FUNC_DTOTAUTO, IO_TYPE_FUNC_DTOTMAN,
                                                                       IO_TYPE_FUNC_TIME, IO_TYPE_FUNC_TIMEAUTO,
                                                                       IO_TYPE_FUNC_TIMEMAN, IO_TYPE_FUNC_DTIME,
                                                                       IO_TYPE_FUNC_DTIMEAUTO, IO_TYPE_FUNC_DTIMEMAN]:
                if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR1] == IO_DI:
                    if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR2] == ind_target:
                        txt = f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tAddress"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
            if data_config.IO_RI_List[Ind].intval[IO_INT_NBYTES] == ind_target:
                txt = f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tEnabled"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.IO_RI_List[Ind].intval[IO_INT_TIMEOUT] == ind_target:
                txt = f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tReset"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
    elif iotype == IO_DO:
        for Ind in range(0, len(data_config.IO_RI_List)):
            if data_config.IO_RI_List[Ind].intval[IO_INT_ADDRTYPE] in [IO_TYPE_FUNC_TOT, IO_TYPE_FUNC_TOTAUTO,
                                                                       IO_TYPE_FUNC_TOTMAN, IO_TYPE_FUNC_DTOT,
                                                                       IO_TYPE_FUNC_DTOTAUTO, IO_TYPE_FUNC_DTOTMAN,
                                                                       IO_TYPE_FUNC_TIME, IO_TYPE_FUNC_TIMEAUTO,
                                                                       IO_TYPE_FUNC_TIMEMAN, IO_TYPE_FUNC_DTIME,
                                                                       IO_TYPE_FUNC_DTIMEAUTO, IO_TYPE_FUNC_DTIMEMAN]:
                if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR1] == IO_DO:
                    if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR2] == ind_target:
                        txt = f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tAddress"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
    elif iotype == IO_AI:
        # campo In dei AO
        for Ind in range(0, len(data_config.IO_AO_List)):
            if data_config.IO_AO_List[Ind].intval[IO_INT_ININD] == ind_target:
                txt = f"IO\t→\tAO\t→\t[{Ind}] {get_io_name(iotype=IO_AI, Ind=Ind)}\t→\tIn"
                _return.append(txt)
                if verbose:
                    logging.info(txt)

        found = run_io_expr_scan(iotype=IO_AI, ind_target=ind_target)
        if found:
            _return.extend(found)

        for Ind in range(0, len(data_config.IO_RI_List)):
            if data_config.IO_RI_List[Ind].intval[IO_INT_ADDRTYPE] in [IO_TYPE_FUNC_TOT, IO_TYPE_FUNC_TOTAUTO,
                                                                       IO_TYPE_FUNC_TOTMAN, IO_TYPE_FUNC_DTOT,
                                                                       IO_TYPE_FUNC_DTOTAUTO, IO_TYPE_FUNC_DTOTMAN,
                                                                       IO_TYPE_FUNC_TIME, IO_TYPE_FUNC_TIMEAUTO,
                                                                       IO_TYPE_FUNC_TIMEMAN, IO_TYPE_FUNC_DTIME,
                                                                       IO_TYPE_FUNC_DTIMEAUTO, IO_TYPE_FUNC_DTIMEMAN]:
                if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR1] == IO_AI:
                    if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR2] == ind_target:
                        txt = f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tAddress"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
    elif iotype == IO_AO:
        for Ind in range(0, len(data_config.IO_AO_List)):
            if data_config.IO_AO_List[Ind].intval[IO_INT_TIMEOUT] == ind_target:
                txt = f"IO\t→\tAO\t→\t[{Ind}] {get_io_name(iotype=IO_AO, Ind=Ind)}\t→\tAO Dual"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
        for Ind in range(0, len(data_config.IO_RI_List)):
            if data_config.IO_RI_List[Ind].intval[IO_INT_ADDRTYPE] in [IO_TYPE_FUNC_TOT, IO_TYPE_FUNC_TOTAUTO,
                                                                       IO_TYPE_FUNC_TOTMAN, IO_TYPE_FUNC_DTOT,
                                                                       IO_TYPE_FUNC_DTOTAUTO, IO_TYPE_FUNC_DTOTMAN,
                                                                       IO_TYPE_FUNC_TIME, IO_TYPE_FUNC_TIMEAUTO,
                                                                       IO_TYPE_FUNC_TIMEMAN, IO_TYPE_FUNC_DTIME,
                                                                       IO_TYPE_FUNC_DTIMEAUTO, IO_TYPE_FUNC_DTIMEMAN]:
                if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR1] == IO_AO:
                    if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR2] == ind_target:
                        txt = f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tAddress"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
    elif iotype == IO_RI:
        for Ind in range(0, len(data_config.IO_RI_List)):
            if data_config.IO_RI_List[Ind].intval[IO_INT_ININD] == ind_target:
                txt = f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tIn"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.IO_RI_List[Ind].intval[IO_INT_ADDRTYPE] in [IO_TYPE_FUNC_TOT, IO_TYPE_FUNC_TOTAUTO,
                                                                       IO_TYPE_FUNC_TOTMAN, IO_TYPE_FUNC_DTOT,
                                                                       IO_TYPE_FUNC_DTOTAUTO, IO_TYPE_FUNC_DTOTMAN,
                                                                       IO_TYPE_FUNC_TIME, IO_TYPE_FUNC_TIMEAUTO,
                                                                       IO_TYPE_FUNC_TIMEMAN, IO_TYPE_FUNC_DTIME,
                                                                       IO_TYPE_FUNC_DTIMEAUTO, IO_TYPE_FUNC_DTIMEMAN]:
                if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR1] == IO_RI:
                    if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR2] == ind_target:
                        txt = f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tAddress"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)

        found = run_io_expr_scan(iotype=IO_RI, ind_target=ind_target, verbose=verbose)
        if found:
            _return.extend(found)
    logging.debug('OUT: run_io_scan')
    return _return


def run_alarm_scan(iotype: int, ind_target: int = None, verbose: bool = False) -> List[str]:
    logging.debug('IN: run_alarm_scan')
    _return = []
    if iotype == IO_DI:
        AlarmParams = data_config.Alarm_Param
        for idx, AlarmParam in enumerate(AlarmParams):
            for _idx, val in enumerate(AlarmParam.intval):
                idx_name = Type_AlarmParam_Map["_intval"][_idx]
                param_type = Type_AlarmParam_Map["intval"][idx_name].get("type", [])
                if iotype in param_type:
                    if val == ind_target:
                        display = Type_AlarmParam_Map["intval"][idx_name]["display"]
                        origin = Type_AlarmParam_Map["intval"][idx_name]["origin"]
                        alarm_name = AlarmParam.name
                        txt = f"{origin.format(idx, alarm_name)}\t→\t{display}"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
    elif iotype == IO_DO:
        AlarmParams = data_config.Alarm_Param
        for idx, AlarmParam in enumerate(AlarmParams):
            for _idx, val in enumerate(AlarmParam.intval):
                idx_name = Type_AlarmParam_Map["_intval"][_idx]
                param_type = Type_AlarmParam_Map["intval"][idx_name].get("type", [])
                if iotype in param_type:
                    if val == ind_target:
                        display = Type_AlarmParam_Map["intval"][idx_name]["display"]
                        origin = Type_AlarmParam_Map["intval"][idx_name]["origin"]
                        alarm_name = AlarmParam.name
                        txt = f"{origin.format(idx, alarm_name)}\t→\t{display}"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
    logging.debug('OUT: run_alarm_scan')
    return _return


def run_motor_scan(iotype: int, ind_target: int = None, verbose: bool = False):
    logging.debug('IN: run_motor_scan')
    _return = []
    if iotype == IO_DI:
        for Ind in range(0, MAX_MOTORE):
            if data_config.Motor_LSInd[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tLS - STOP"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_LS2Ind[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tLS2 - START"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_TRInd[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tTR"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_TR2Ind[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tTR2"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_StatInd[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tSTAT"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_StartingInd[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tSTARTING"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
    elif iotype == IO_DO:
        for Ind in range(0, MAX_MOTORE):
            if data_config.Motor_CmdInd[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tCMD"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_Cmd1Ind[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tCMD1"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_Cmd2Ind[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tCMD2"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_Cmd3Ind[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tCMD3"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
    logging.debug('OUT: run_motor_scan')
    return _return


def run_maintenance_scan(iotype: int, ind_target: int = None, verbose: bool = False) -> List[str]:
    logging.debug('IN: run_maintenance_scan')
    _return = []
    if iotype == IO_DI:
        MaintParams = data_config.Maint_Param
        for idx, MaintParam in enumerate(MaintParams):
            for _idx, val in enumerate(MaintParam.intval):
                idx_name = Type_MaintParam_Map["_intval"][_idx]
                param_type = Type_MaintParam_Map["intval"][idx_name].get("type", [])
                if iotype in param_type:
                    if val == ind_target:
                        display = Type_MaintParam_Map["intval"][idx_name]["display"]
                        origin = Type_MaintParam_Map["intval"][idx_name]["origin"]
                        maint_name = MaintParam.name
                        txt = f"{origin.format(idx, maint_name)}\t→\t{display}"
                        _return.append(txt)
                        if verbose:
                            logging.info(txt)
    elif iotype == IO_DO:
        for Ind in range(0, MAX_MAINT):
            if data_config.Motor_CmdInd[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tCMD"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_Cmd1Ind[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tCMD1"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_Cmd2Ind[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tCMD2"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
            if data_config.Motor_Cmd3Ind[Ind] == ind_target:
                txt = f"Motor\t→\t{Ind + 1}\t→\tCMD3"
                _return.append(txt)
                if verbose:
                    logging.info(txt)
    logging.debug('OUT: run_maintenance_scan')
    return _return


def decode_sys_addr_name(ind_target: int):
    if not isinstance(ind_target, int) or ind_target < BASE_AXIS:
        return None

    systyp = ind_target // BASE_AXIS
    objelemind = ind_target % BASE_AXIS

    # split oggetto / elemento
    if 1 <= systyp <= 7:
        objind = objelemind % AXIS_GROUP_STEP
        elemind = objelemind // AXIS_GROUP_STEP
    elif 8 <= systyp <= 10:
        objind = objelemind % ALARM_GROUP_STEP
        elemind = objelemind // ALARM_GROUP_STEP
    else:
        return None

    # nome tipo invertendo SYSTEM_TYPE
    systyp_name = next((k for k, v in SYSTEM_TYPE.items() if v == systyp), None)
    if not systyp_name:
        return None

    # helper: safe index su lista ordine
    def _name_from_order(order_list, idx, fallback_prefix="ELEM"):
        if isinstance(order_list, (list, tuple)) and 0 <= idx < len(order_list):
            return str(order_list[idx]).upper()
        return f"{fallback_prefix}{idx}"

    # ---- AXIS ----
    if systyp_name == "AXIS":
        elem_name = _name_from_order(AXIS_GROUPS_ORDER, elemind)
        return f"{systyp_name}[{get_axis_name(objind)}].{elem_name}"

    # ---- ALARM ----
    if systyp_name == "ALARM":
        elem_name = _name_from_order(ALARM_GROUPS_ORDER, elemind)
        return f"{systyp_name}[{objind}].{elem_name}"

    # ---- MAINT / BOOLSYSTEM (se le hai) ----
    # Se non esistono nel tuo file costants, questa parte puoi toglierla.
    if systyp_name == "MAINT":
        try:
            elem_name = _name_from_order(MAINT_GROUPS_ORDER, elemind)
        except NameError:
            elem_name = f"ELEM{elemind}"
        return f"{systyp_name}[{objind}].{elem_name}"

    if systyp_name == "BOOLSYSTEM":
        try:
            elem_name = _name_from_order(BOOLSYSTEM_GROUPS_ORDER, elemind)
        except NameError:
            elem_name = f"ELEM{elemind}"
        return f"{systyp_name}[{objind}].{elem_name}"

    # fallback altri tipi
    return f"{systyp_name}[{objind}].ELEM{elemind}"


def get_sys_addr(group: str, ind_target: int) -> Optional[int]:
    """
    Ritorna l'indirizzo SYSTEM (>=2048) corrispondente a un dato gruppo e indice.

    Esempio:
        get_sys_addr("ALARM", 97) -> 16481
        get_sys_addr("AXIS.UP", 1) -> 2113

    Ritorna None se input non valido.
    """

    if not isinstance(group, str):
        return None

    group = group.strip().upper()
    if not group:
        return None

    parts = group.split(".")
    sys_type = parts[0]

    # indice valido?
    try:
        idx = int(ind_target)
    except Exception:
        return None

    if idx < 0:
        return None

    # tipo valido?
    type_id = SYSTEM_TYPE.get(sys_type)
    if type_id is None:
        return None

    # campo (se presente)
    field = parts[1] if len(parts) == 2 else None

    # DEFAULT FIELD
    if field is None:
        default_field = {
            "AXIS": "MOVING",
            "ALARM": "VAL",
            "MAINT": "VAL",
        }.get(sys_type)

        if default_field is None:
            return None

        field = default_field

    # Mappa FIELD → field_id
    # Per ALARM e MAINT step = 256
    # Per AXIS step = 64

    if sys_type == "ALARM":
        field_map = {
            "VAL": 0,
            "ACK": 1,
            "ENA": 2,
        }
        step = ALARM_GROUP_STEP

    elif sys_type == "MAINT":
        field_map = {
            "VAL": 0,
            "ACK": 1,
        }
        step = ALARM_GROUP_STEP

    elif sys_type == "AXIS":
        field_map = {
            "MOVING": 0,
            "UP": 1,
            "DOWN": 2,
            "MAX": 3,
            "MIN": 4,
        }
        step = AXIS_GROUP_STEP

    else:
        return None

    field_id = field_map.get(field)
    if field_id is None:
        return None

    base = BASE_AXIS * type_id

    return base + step * field_id + idx

def get_expr_from_di(ind: int) -> List[Tuple[int, int, int]]:
    """
    Ritorna una lista di tuple (not_val, opnd_val, oper_val) per ogni gruppo
    di espressione associato al DI specificato.
    """
    expr_list = []
    if 0 <= ind < len(data_config.IO_DI_List):
        di_param = data_config.IO_DI_List[ind]
        if di_param.intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
            exprintval = di_param.exprintval
            if len(exprintval) > 1:
                for i in range(1, len(exprintval), 3):
                    if i + 2 < len(exprintval):
                        not_val = exprintval[i]
                        opnd_val = exprintval[i + 1]
                        oper_val = exprintval[i + 2]
                        expr_list.append((not_val, opnd_val, oper_val))
        else:
            exprintval = di_param.exprintval
            if len(exprintval) > 1:
                for i in range(1, len(exprintval), 3):
                    if i + 2 < len(exprintval):
                        not_val = exprintval[i]
                        opnd_val = exprintval[i + 1]
                        oper_val = exprintval[i + 2]
                        expr_list.append((not_val, opnd_val, oper_val))

    return expr_list


def run_free_scan(iotype: int):
    """
    Scansiona tutti gli IO di un certo tipo (DI/DO/AI/AO)
    e per ogni elemento con nome vuoto o 'FREE', esegue una ricerca completa.
    """
    if iotype == IO_DI:
        io_list = data_config.IO_DI_List
        label = "DI"
    elif iotype == IO_DO:
        io_list = data_config.IO_DO_List
        label = "DO"
    elif iotype == IO_AI:
        io_list = data_config.IO_AI_List
        label = "AI"
    elif iotype == IO_AO:
        io_list = data_config.IO_AO_List
        label = "AO"
    elif iotype == IO_RI:
        io_list = data_config.IO_RI_List
        label = "RI"
    else:
        logging.info(f"[ERRORE] Tipo IO sconosciuto: {iotype}")
        return

    if not io_list:
        logging.info(f"Nessun {label} trovato nel data_config.")
        return

    for i, param in enumerate(io_list):
        if param.name == "" or param.name.strip().upper() == "FREE":
            run_io_search(iotype=iotype, Ind=i, verbose=True)


def run_io_search(iotype: int, Ind: Optional[int] = None, verbose: bool = False) -> List[str]:
    logging.debug('IN: run_io_search')
    _return = []
    if Ind == -1:
        if iotype == IO_DI:
            for _Ind in range(0, len(data_config.IO_DI_List)):
                data = run_io_search(iotype=IO_DI, Ind=_Ind, verbose=False)
                if data:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)}")  # senza parentesi per differenziare da RI
                    _return.extend(data)
                else:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)} unused")  # senza parentesi per differenziare da RI
        elif iotype == IO_DO:
            for _Ind in range(0, len(data_config.IO_DO_List)):
                data = run_io_search(iotype=IO_DO, Ind=_Ind, verbose=False)
                if data:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)}")  # senza parentesi per differenziare da RI
                    _return.extend(data)
                else:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)} unused")  # senza parentesi per differenziare da RI
        elif iotype == IO_AI:
            for _Ind in range(0, len(data_config.IO_AI_List)):
                data = run_io_search(iotype=IO_AI, Ind=_Ind, verbose=False)
                if data:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)}")  # senza parentesi per differenziare da RI
                    _return.extend(data)
                else:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)} unused")  # senza parentesi per differenziare da RI
        elif iotype == IO_AO:
            for _Ind in range(0, len(data_config.IO_AO_List)):
                data = run_io_search(iotype=IO_AO, Ind=_Ind, verbose=False)
                if data:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)}")  # senza parentesi per differenziare da RI
                    _return.extend(data)
                else:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)} unused")  # senza parentesi per differenziare da RI
        elif iotype == IO_RI:
            for _Ind in range(0, len(data_config.IO_RI_List)):
                data = run_io_search(iotype=IO_RI, Ind=_Ind, verbose=verbose)
                if data:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)}")  # senza parentesi per differenziare da RI
                    _return.extend(data)
                else:
                    _return.append(f"--- [{_Ind}] {get_io_name(iotype=iotype, Ind=_Ind)} unused")  # senza parentesi per differenziare da RI
        for item in _return:
            logging.info(item)
    elif iotype == IO_DI:
        _return.extend(run_io_scan(iotype=IO_DI, ind_target=Ind, verbose=verbose))
        _return.extend(run_params_scan(iotype=IO_DI, ind_target=Ind, verbose=verbose))
        _return.extend(run_motor_scan(iotype=IO_DI, ind_target=Ind, verbose=verbose))
        _return.extend(run_axis_scan(iotype=IO_DI, ind_target=Ind, axisInd=None, verbose=verbose))
        _return.extend(run_input_scan(iotype=IO_DI, ind_target=Ind, inputInd=None, verbose=verbose))
        _return.extend(run_output_scan(iotype=IO_DI, ind_target=Ind, outputInd=None, verbose=verbose))
        _return.extend(run_feedback_scan(iotype=IO_DI, ind_target=Ind, feedbackInd=None, verbose=verbose))
        _return.extend(run_alarm_scan(iotype=IO_DI, ind_target=Ind, verbose=verbose))
        _return.extend(run_maintenance_scan(iotype=IO_DI, ind_target=Ind, verbose=verbose))
    elif iotype == IO_DO:
        _return.extend(run_io_scan(iotype=IO_DO, ind_target=Ind, verbose=verbose))
        _return.extend(run_params_scan(iotype=IO_DO, ind_target=Ind, verbose=verbose))
        _return.extend(run_motor_scan(iotype=IO_DO, ind_target=Ind, verbose=verbose))
        # run_axis_scan(iotype=IO_DO, ind_target=Ind, axisInd=None)
        # run_input_scan(iotype=IO_DO, ind_target=Ind, inputInd=None)
        _return.extend(run_output_scan(iotype=IO_DO, ind_target=Ind, outputInd=None, verbose=verbose))
        # run_feedback_scan(iotype=IO_DO, ind_target=Ind, feedbackInd=None)
        _return.extend(run_alarm_scan(iotype=IO_DO, ind_target=Ind, verbose=verbose))
        # run_maintenance_scan(iotype=IO_DO, ind_target=Ind)
    elif iotype == IO_AI:
        _return.extend(run_io_scan(iotype=IO_AI, ind_target=Ind, verbose=verbose))
        _return.extend(run_params_scan(iotype=IO_AI, ind_target=Ind, verbose=verbose))
        # run_motor_scan(iotype=IO_AI, ind_target=Ind)
        # run_axis_scan(iotype=IO_AI, ind_target=Ind, axisInd=None)
        _return.extend(run_input_scan(iotype=IO_AI, ind_target=Ind, inputInd=None, verbose=verbose))
        _return.extend(run_output_scan(iotype=IO_AI, ind_target=Ind, outputInd=None, verbose=verbose))
        _return.extend(run_feedback_scan(iotype=IO_AI, ind_target=Ind, feedbackInd=None, verbose=verbose))
        # run_alarm_scan(iotype=IO_AI, ind_target=Ind)
        # run_maintenance_scan(iotype=IO_AI, ind_target=Ind)
    elif iotype == IO_AO:
        _return.extend(run_io_scan(iotype=IO_AO, ind_target=Ind, verbose=verbose))
        # run_params_scan(iotype=IO_AO, ind_target=Ind)
        # run_motor_scan(iotype=IO_AO, ind_target=Ind)
        # run_axis_scan(iotype=IO_AO, ind_target=Ind, axisInd=None)
        _return.extend(run_input_scan(iotype=IO_AO, ind_target=Ind, inputInd=None, verbose=verbose))
        _return.extend(run_output_scan(iotype=IO_AO, ind_target=Ind, outputInd=None, verbose=verbose))
        # run_feedback_scan(iotype=IO_AO, ind_target=Ind, feedbackInd=None)
        # run_alarm_scan(iotype=IO_AO, ind_target=Ind)
        # run_maintenance_scan(iotype=IO_AO, ind_target=Ind)
    elif iotype == IO_RI:
        _return.extend(run_io_scan(iotype=IO_RI, ind_target=Ind, verbose=verbose))
        # run_params_scan(iotype=IO_RI, ind_target=Ind)
        # run_motor_scan(iotype=IO_RI, ind_target=Ind)
        # run_axis_scan(iotype=IO_RI, ind_target=Ind, axisInd=None)
        # run_input_scan(iotype=IO_RI, ind_target=Ind, inputInd=None)
        # run_output_scan(iotype=IO_RI, ind_target=Ind, outputInd=None)
        # run_feedback_scan(iotype=IO_RI, ind_target=Ind, feedbackInd=None)
        # run_alarm_scan(iotype=IO_RI, ind_target=Ind)
        # run_maintenance_scan(iotype=IO_RI, ind_target=Ind)
    logging.debug('OUT: run_io_search')
    return _return


def custom_function():
    """Controlla coerenza flag booleani e riferimenti I/O per SMAX, SHH, SH, SL, SLL, SMIN, SH0, SL0."""
    logger.debug("IN: custom_function")

    def check_axis_flag() -> list[str]:
        """
        Controlla limiti e flag per ogni asse.
        Stampa warning prima del gruppo di riferimenti.
        """
        logging.info("🔍 Avvio controllo flag assi...")

        def _axis_label_from_int_idx(int_idx: int) -> str:
            try:
                key = Type_AxisParam_Map["_intval"][int_idx]
                return str(Type_AxisParam_Map["intval"][key].get("display", key))
            except Exception:
                return "??"

        def _axis_label_from_bool_idx(bool_idx: int) -> str:
            try:
                key = Type_AxisParam_Map["_boolval"][bool_idx]
                return str(Type_AxisParam_Map["boolval"][key].get("display", key))
            except Exception:
                return "??"

        axis_pairs = [
            (ASSE_INT_INDSHH, ASSE_BOOL_ENABSHH, ASSE_REAL_SHH),
            (ASSE_INT_INDSH, ASSE_BOOL_ENABSH, ASSE_REAL_SH),
            (ASSE_INT_INDSL, ASSE_BOOL_ENABSL, ASSE_REAL_SL),
            (ASSE_INT_INDSLL, ASSE_BOOL_ENABSLL, ASSE_REAL_SLL),
            (ASSE_INT_INDSH0, ASSE_BOOL_ENABSH0, ASSE_REAL_SH0),
            (ASSE_INT_INDSL0, ASSE_BOOL_ENABSL0, ASSE_REAL_SL0),
        ]

        AXIS_SYS_CODE = {
            "HH": 7, "H": 8, "L": 9, "LL": 10, "H0": 11, "L0": 12,
            "SMAX": 3, "SMIN": 4,
        }

        bool_only = [
            (ASSE_BOOL_ENABSMAX, "SMAX"),
            (ASSE_BOOL_ENABSMIN, "SMIN"),
        ]

        def _sys_index_for(axisInd: int, label: str) -> int:
            code = AXIS_SYS_CODE.get(label)
            if code is None:
                return -1
            return BASE_AXIS * 1 + (code * AXIS_GROUP_STEP + axisInd)

        out_lines: list[str] = []

        for axisInd in range(MAX_ASSE):
            try:
                AxisParamIntVals = data_config.Axis_Param[axisInd].intval
                AxisParamBoolVals = data_config.Axis_Param[axisInd].boolval
                AxisParamRealVals = data_config.Axis_Param[axisInd].realval
            except Exception:
                logging.critical(f"Errore lettura parametri asse {axisInd}")
                continue

            axis_name = get_axis_name(Ind=axisInd)
            MinLS = data_config.Axis_Param[axisInd].realval[ASSE_REAL_SMIN]
            MaxLS = data_config.Axis_Param[axisInd].realval[ASSE_REAL_SMAX]
            local_buf: list[str] = []

            for int_idx, bool_idx, real_idx in axis_pairs:
                if int_idx >= len(AxisParamIntVals) or bool_idx >= len(AxisParamBoolVals):
                    continue

                di_val = AxisParamIntVals[int_idx]
                flag = AxisParamBoolVals[bool_idx]
                label = _axis_label_from_int_idx(int_idx)
                sys_idx = _sys_index_for(axisInd, label)
                value = ''
                refs: list[str] = []
                try:
                    if di_val > 0:
                        refs.extend(run_io_search(iotype=IO_DI, Ind=di_val, verbose=False) or [])
                except Exception:
                    pass
                try:
                    if sys_idx >= 0:
                        refs.extend(run_io_search(iotype=IO_DI, Ind=sys_idx, verbose=False) or [])
                except Exception:
                    pass

                value = AxisParamRealVals[real_idx]

                if refs or di_val > 0:
                    # ⚠️ warning PRIMA
                    if not flag and (di_val > 0 or refs):
                        local_buf.append(
                            f"  ⚠️  Flag {label} disattivo ma {label}={di_val if di_val > 0 else 'SYS'} è impostato/usato")

                    # header label
                    local_buf.append(f"    ↳ Axes\t→\t[{axisInd}]{axis_name}\t→\t{label}" + (f"\t({value})" if value else ""))
                    for ref in refs:
                        local_buf.append(f"        ↳ {ref}")

            for bool_idx, sys_name in bool_only:
                if bool_idx >= len(AxisParamBoolVals):
                    continue
                flag = AxisParamBoolVals[bool_idx]
                sys_idx = _sys_index_for(axisInd, sys_name)

                refs: list[str] = []
                try:
                    if sys_idx >= 0:
                        refs.extend(run_io_search(iotype=IO_DI, Ind=sys_idx, verbose=False) or [])
                except Exception:
                    pass

                if refs:
                    if not flag:
                        label = _axis_label_from_bool_idx(bool_idx)
                        local_buf.append(f"  ⚠️  Flag {label} disattivo ma {label} è usato")
                    local_buf.append(f"    ↳ Axes\t→\t[{axisInd}]{axis_name}\t→\t{sys_name}")
                    for ref in refs:
                        local_buf.append(f"        ↳ {ref}")

            if local_buf:
                logging.warning(f"\n[ASSE {axisInd:02d}] {axis_name}\t({MinLS} , {MaxLS})")
                logging.warning("\n".join(local_buf))
                out_lines.append(f"[ASSE {axisInd:02d}] {axis_name}\t({MinLS} , {MaxLS})")
                out_lines.extend(local_buf)

        logging.info("🔍 Fine controllo flag assi.")
        return out_lines

    def check_duplicate_do_ao_usage():
        """
        Controlla se una DO/AO è referenziata in più punti nel progetto.
        Usa run_io_scan per verificare dove viene utilizzata ogni uscita.
        """
        logging.info(f'🔍Avvio controllo duplicati DO AO...')
        duplicates = {}

        for iotype, label in [(IO_DO, "DO"), (IO_AO, "AO")]:
            io_list = data_config.IO_DO_List if iotype == IO_DO else data_config.IO_AO_List

            for idx in range(len(io_list)):
                used_in = run_io_search(iotype=iotype, Ind=idx, verbose=False)
                if len(used_in) > 1:
                    io_name = get_io_name(iotype=iotype, Ind=idx)
                    duplicates[io_name or f"{label}[{idx}]"] = used_in
                    logging.warning(f"⚠️ {label}[{idx}] {io_name or ''} usato in più punti:")
                    for u in used_in:
                        logging.warning(f"   ↳ {u}")
        logging.info(f'🔍Fine controllo duplicati DO AO...')
        return duplicates

    def check_duplicate_obj_usage(verbose: bool = True) -> dict:
        """
        Controlla se input, output o feedback sono usati in più assi diversi.
        Restituisce un dict con le duplicazioni trovate.
        """
        logging.info(f'🔍Avvio controllo duplicati Input/Output/Feedback...')
        result = {
            "feedback": {},
            "input": {},
            "output": {}
        }

        for axisInd in range(0, MAX_ASSE):
            axis_name = data_config.Axis_Name[axisInd]

            # --- FEEDBACK ---
            fb_indices = [
                data_config.Axis_Param[axisInd].intval[ASSE_INT_FEEDBACK],
                data_config.Axis_Param[axisInd].intval[ASSE_INT_ALTFB]
            ]
            for fb in fb_indices:
                if fb != -1:
                    result["feedback"].setdefault(fb, []).append(f'[{axisInd}]{axis_name}')

            # --- INPUT ---
            input_indices = [
                data_config.Axis_Param[axisInd].intval[ASSE_INT_INPUT],
                data_config.Axis_Param[axisInd].intval[ASSE_INT_INPUT2],
                data_config.Axis_Param[axisInd].intval[ASSE_INT_INPUT3],
                data_config.Axis_Param[axisInd].intval[ASSE_INT_INPUT4],
            ]
            for inp in input_indices:
                if inp != -1:
                    result["input"].setdefault(inp, []).append(f'[{axisInd}]{axis_name}')

            # --- OUTPUT ---
            output_indices = [
                data_config.Axis_Param[axisInd].intval[ASSE_INT_OUTPUT1],
                data_config.Axis_Param[axisInd].intval[ASSE_INT_OUTPUT2],
                data_config.Axis_Param[axisInd].intval[ASSE_INT_OUTPUT3],
                data_config.Axis_Param[axisInd].intval[ASSE_INT_OUTPUT4],
            ]
            for outp in output_indices:
                if outp != -1:
                    result["output"].setdefault(outp, []).append(f'[{axisInd}]{axis_name}')

        # --- Filtra solo duplicati (usati in più di un asse) ---
        duplicates = {
            "feedback": {k: v for k, v in result["feedback"].items() if len(v) > 1},
            "input": {k: v for k, v in result["input"].items() if len(v) > 1},
            "output": {k: v for k, v in result["output"].items() if len(v) > 1},
        }

        if verbose:
            if any(duplicates.values()):
                logging.warning("⚠️ Duplicazioni trovate:")
                for cat, items in duplicates.items():
                    for ind, axes in items.items():
                        logging.warning(f" - {cat.upper()}[{ind}] usato in: {', '.join(axes)}")
        logging.info('🔍 Fine controllo duplicati Input/Output/Feedback.')
        return duplicates

    def clean_di_axis_check() -> None:
        logging.info("🔍 Avvio controllo axis_flag_checks...")
        major, minor, patch, build = get_pgsx_version()
        for axisInd in range(0, MAX_ASSE):
            AxisParamIntVals = data_config.Axis_Param[axisInd].intval
            to_check = [ASSE_INT_INDSHH, ASSE_INT_INDSH, ASSE_INT_INDSL, ASSE_INT_INDSLL, ASSE_INT_INDSH0, ASSE_INT_INDSL0]
            if patch >= 53:
                to_check.extend([ASSE_INT_OPTPARAM1IND, ASSE_INT_OPTPARAM2IND, ASSE_INT_OPTPARAM3IND])
            else:
                try:
                    to_check.extend([ASSE_INT_FREE_71, ASSE_INT_FREE_72, ASSE_INT_OPTPARAM1IND, ASSE_INT_OPTPARAM2IND, ASSE_INT_OPTPARAM3IND])
                except NameError:
                    logging.debug("⚠️ Alcuni parametri opzionali non sono definiti nella versione corrente.")  # TODO: gestire meglio
                    pass
            for idx in to_check:
                idx_name = Type_AxisParam_Map["_intval"][idx]
                if AxisParamIntVals[idx] != -1:
                    display = Type_AxisParam_Map["intval"][idx_name]["display"]
                    origin = Type_AxisParam_Map["intval"][idx_name]["origin"]
                    axis_name = get_axis_name(Ind=axisInd)
                    logging.warning(f"⚠️ {origin.format(axisInd, axis_name)}\t→\t{display}\t[{AxisParamIntVals[idx]}] {get_io_name(iotype=IO_DI, Ind=AxisParamIntVals[idx])}")
        logging.info("🔍 Fine controllo axis_flag_checks...")

    def duplicate_io_address(verbose: bool = True) -> dict[str, dict[tuple[str, int, int], list[tuple[int, str]]]]:
        """
        Cerca IO con indirizzi duplicati per ciascun tipo (DI, DO, AI, AO),
        considerando anche il tipo logico (IO_TYPE_CALC, IO_TYPE_PNET, IO_TYPE_CAN...).

        Raggruppa i duplicati per chiave (tipo, addr1, addr2):
          {
            "DI": {
                ("CALC", 3, 5): [(12,"SENSOR_UP_LIMIT"), (98,"SAFETY_INPUT_UP")],
                ("PNET", 4, 1): [(15,"ENDSTOP_DOWN"), (34,"DOOR_SENS")]
            },
            ...
          }
        """
        logging.info("🔍 Avvio controllo indirizzi duplicati...")

        # --- helper interno ---
        def _check(io_list, label: str):
            duplicates: dict[str, dict[tuple[str, int, int], list[tuple[int, str]]]] = {}
            addr_map: dict[tuple[str, int, int], list[tuple[int, str]]] = {}

            for i, param in enumerate(io_list):
                if not hasattr(param, "intval"):
                    continue

                # --- recupera indirizzi ---
                addr1 = param.intval[IO_INT_ADDR1]
                addr2 = param.intval[IO_INT_ADDR2]
                addr_type_id = param.intval[IO_INT_ADDRTYPE] if len(param.intval) > IO_INT_ADDRTYPE else -1

                # --- converte in stringa tramite mappa ---

                name = (param.name or "").strip().upper()

                # ignora IO vuoti o placeholder
                if not name or name in ("FREE", "NONE", "-", "NULL"):
                    continue
                # ignora tipi
                if addr_type_id not in [IO_TYPE_PNET, IO_TYPE_CAN, IO_TYPE_SW]:
                    continue
                # ignora indirizzi invalidi o liberi
                if (addr1, addr2) in [(-1, -1), (0, 0)] or (addr1 in (-1, 0) and addr2 in (-1, 0)):
                    continue

                # --- chiave completa (tipo + indirizzo) ---
                key = (addr_type_id, addr1, addr2)
                addr_map.setdefault(key, []).append((i, name))

            # --- estrai solo duplicati ---
            dup_group = {k: v for k, v in addr_map.items() if len(v) > 1}
            if dup_group:
                duplicates[label] = dup_group
                if verbose:
                    logging.warning(f"\n⚠️  Duplicati trovati in {label}:")
                    # ordina per tipo per renderlo più leggibile
                    for (tp, a1, a2), entries in sorted(dup_group.items(), key=lambda x: x[0]):
                        joined = ", ".join([f"[{idx}] {nm}" for idx, nm in entries])
                        logging.warning(
                            f"   → {'PNET' if tp == IO_TYPE_PNET else 'CAN' if tp == IO_TYPE_CAN else 'SW'} {a1}.{a2:<3} → {joined}")

        _check(data_config.IO_DI_List, "DI")
        _check(data_config.IO_AI_List, "AI")
        _check(data_config.IO_DO_List, "DO")
        _check(data_config.IO_AO_List, "AO")
        logging.info("🔍 Fine controllo indirizzi duplicati...")

    def check_forbidden_ao_do_usage() -> None:
        logging.info("🔍 Avvio controllo indirizzi safety...")
        fAddresses = []

        def build_forbidden_addresses(start: int, next_address: int, modules: int) -> list[str]:
            """
            Costruisce la lista degli indirizzi proibiti per AO/DO safety.
            Ogni indirizzo rappresenta 1 byte (.0..7).
            - start: indirizzo iniziale
            - next_address: numero di indirizzi per modulo
            - modules: quanti moduli totali generare
            """
            total_addresses = next_address * modules
            blocco = [f"{addr}" for addr in range(start, start + total_addresses)]
            fAddresses.extend(blocco)
            return blocco

        build_forbidden_addresses(1100, 5, 2)  # A_SF
        for Ind in range(0, len(data_config.IO_DI_List)):
            if data_config.IO_DI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_PNET:
                addr1 = data_config.IO_DI_List[Ind].intval[IO_INT_ADDR1]
                # addr2 = data_config.IO_DI_List[Ind].intval[IO_INT_ADDR2]
                addr_str = f"{addr1}"  # {addr2}"
                if addr_str in fAddresses:
                    io_name = get_io_name(iotype=IO_DI, Ind=Ind)
                    logging.warning(f"⚠️ Safety non permesso in DI [{Ind}] {io_name} at address {addr_str}")
        for Ind in range(0, len(data_config.IO_AI_List)):
            if data_config.IO_AI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_PNET:
                addr1 = data_config.IO_AI_List[Ind].intval[IO_INT_ADDR1]
                # addr2 = data_config.IO_AI_List[Ind].intval[IO_INT_ADDR2]
                addr_str = f"{addr1}"  # {addr2}"
                if addr_str in fAddresses:
                    io_name = get_io_name(iotype=IO_AI, Ind=Ind)
                    logging.warning(f"⚠️  Safety non permesso in AI [{Ind}] {io_name} at address {addr_str}")
        for Ind in range(0, len(data_config.IO_DO_List)):
            if data_config.IO_DO_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_PNET:
                addr1 = data_config.IO_DO_List[Ind].intval[IO_INT_ADDR1]
                # addr2 = data_config.IO_DO_List[Ind].intval[IO_INT_ADDR2]
                addr_str = f"{addr1}"  # {addr2}"
                if addr_str in fAddresses:
                    io_name = get_io_name(iotype=IO_DO, Ind=Ind)
                    logging.warning(f"⚠️ Safety non permesso in DO [{Ind}] {io_name} at address {addr_str}")
        for Ind in range(0, len(data_config.IO_AO_List)):
            if data_config.IO_AO_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_PNET:
                addr1 = data_config.IO_AO_List[Ind].intval[IO_INT_ADDR1]
                # addr2 = data_config.IO_AO_List[Ind].intval[IO_INT_ADDR2]
                addr_str = f"{addr1}"  # {addr2}"
                if addr_str in fAddresses:
                    io_name = get_io_name(iotype=IO_AO, Ind=Ind)
                    logging.warning(f"⚠️ Safety non permesso in AO [{Ind}] {io_name} at address {addr_str}")
        logging.info("🔍 Fine controllo indirizzi safety...")

    def check_axis_um() -> list[tuple[int, str, int, int, str]]:
        """
        Controlla che per ogni asse il tipo di misura (ASSE_INT_TIPOMISURA)
        coincida con quello definito nel Feedback (FB_INT_TIPOMISURA).

        Se diversi, li stampa e li aggiunge in lista.
        Restituisce:
            [(index, axis_name, tipo_asse, tipo_fb, fb_name), ...]
        """
        logging.info("🔍 Avvio controllo unità di misura assi...")
        mismatches: list[tuple[int, str, int, int, str]] = []

        for axisInd in range(0, MAX_ASSE):
            axis = data_config.Axis_Param[axisInd]
            axis_name = data_config.Axis_Name[axisInd] or f"AXIS_{axisInd}"
            tipo_asse = axis.intval[ASSE_INT_TIPOMISURA]

            # --- Feedback principale ---
            fb_ind = axis.intval[ASSE_INT_FEEDBACK]
            if fb_ind != -1:
                fb = data_config.Feedback_Param[fb_ind]
                tipo_fb = fb.intval[FB_INT_TIPOMISURA]
                if tipo_asse != tipo_fb:
                    mismatches.append((axisInd, axis_name, tipo_asse, tipo_fb, fb_ind))

            # --- Feedback alternativo ---
            alt_fb_ind = axis.intval[ASSE_INT_ALTFB]
            if alt_fb_ind != -1:
                alt_fb = data_config.Feedback_Param[alt_fb_ind]
                tipo_fb_alt = alt_fb.intval[FB_INT_TIPOMISURA]
                if tipo_asse != tipo_fb_alt:
                    mismatches.append((axisInd, axis_name, tipo_asse, tipo_fb_alt, alt_fb_ind))

        if mismatches:
            logging.warning(f"\n⚠️  Assi con tipo misura diverso (ASSE_INT_TIPOMISURA ≠ FB_INT_TIPOMISURA):")
            for idx, axis_name, t_ass, t_fb, fb_name in mismatches:
                logging.warning(f"   → [{idx:02d}] {axis_name:<20} ASSE={t_ass:<3}  FB={t_fb:<3}  ({fb_name})")

        logging.info("🔍 Fine controllo unità di misura assi.")
        return mismatches

    def check_duplicate_funaxis() -> dict[int, list[int]]:
        """
        Controlla se lo stesso asse è assegnato a più Function Index (FunInd).

        Cerca duplicati in data_config.AxisFunInd, ignorando i valori -1.
        Restituisce un dict:
            { axis_index: [funInd1, funInd2, ...], ... }
        """
        logging.info("🔍 Avvio controllo duplicati AxisFunInd...")
        duplicates: dict[int, list[int]] = {}
        seen: dict[int, int] = {}

        for funInd in range(0, MAX_ASSEFUNIND):
            axisInd = data_config.AxisFunInd[funInd]
            if axisInd == -1:
                continue  # ignora slot vuoti

            if axisInd in seen:
                # trovato duplicato → aggiungi entrambi
                if axisInd not in duplicates:
                    duplicates[axisInd] = [seen[axisInd]]
                duplicates[axisInd].append(funInd)
            else:
                seen[axisInd] = funInd

        if duplicates:
            logging.warning("\n⚠️  Duplicati trovati in AxisFunInd:")
            for axisInd, fun_list in duplicates.items():
                axis_name = getattr(data_config.Axis_Param[axisInd], "name", f"AXIS[{axisInd}]")
                fun_str = ", ".join([f"{Type_AxisFunInd[fi]}" for fi in fun_list])
                logging.warning(f"   → {axis_name:<20} ({axisInd}) usato in FunInd: {fun_str}")

        logging.info("🔍 Fine controllo duplicati AxisFunInd.")
        return duplicates

    def check_lat_sup() -> None:
        logging.info("🔍 Avvio controllo supporti laterali")
        _ = [FUN_AXIS_PRESIDESUPP, FUN_AXIS_BENDSIDESUPP]
        maxSupp = 0.0
        for i in _:
            if data_config.AxisFunInd[i] == -1:
                logging.warning("Indice non configurato in Params > Functions")
            else:
                axis = data_config.Axis_Param[data_config.AxisFunInd[i]]
                axis_name = data_config.Axis_Name[data_config.AxisFunInd[i]] or f"AXIS_{data_config.AxisFunInd[i]}"
                tipo_asse = axis.intval[ASSE_INT_TIPOMISURA]
                if tipo_asse != MISURA_GRAD:
                    logging.warning(f"⚠️ [{data_config.AxisFunInd[i]}]{axis_name} non ha il tipo di misura GRAD")
                if data_config.Axis_Param[data_config.AxisFunInd[i]].intval[ASSE_INT_FEEDBACK] != -1:
                    axis_feedback = data_config.Feedback_Param[data_config.Axis_Param[data_config.AxisFunInd[i]].intval[ASSE_INT_FEEDBACK]]
                    tipo_feedback = axis_feedback.intval[FB_INT_TIPOMISURA]
                    if tipo_feedback != MISURA_GRAD:
                        logging.warning(f"⚠️ [{data_config.AxisFunInd[i]}]{axis_name} il feedback non ha il tipo di misura GRAD")
                    if axis_feedback.realval[FB_REAL_SCALEINF] not in (180.0, -180.0) and axis_feedback.realval[FB_REAL_SCALESUP] not in (180.0, -180.0):
                        logging.warning(f"⚠️ [{data_config.AxisFunInd[i]}]{axis_name} il feedback non ha scala -180°/+180° ma a {axis_feedback.realval[FB_REAL_SCALEINF]} e {axis_feedback.realval[FB_REAL_SCALESUP]}")
                if axis.boolval[ASSE_BOOL_MANSPDOWN]:
                    logging.warning(f"⚠️ [{data_config.AxisFunInd[i]}]{axis_name} ha il flag MANSPDOWN attivo!")
                if maxSupp == 0.0:
                    maxSupp = axis.realval[ASSE_REAL_SMAX]
                else:
                    if axis.realval[ASSE_REAL_SMAX] != maxSupp:
                        logging.warning(f"⚠️ [{data_config.AxisFunInd[i]}]{axis_name} ha SMax ({maxSupp}) diverso dagli altri supporti laterali!")
                    if axis.realval[ASSE_REAL_SMAX] > maxSupp:
                        maxSupp = axis.realval[ASSE_REAL_SMAX]
        if data_config.ParamReal[REAL_LATSUPQ0] != maxSupp and data_config.ParamReal[REAL_LATSUPQ0] < maxSupp - 5.0:
            logging.warning(f"⚠️ Config\t→\tLat\t→\tLATSUPQ0 deve essere impostato a {maxSupp} o leggermente meno")
        if data_config.ParamReal[REAL_LATSUPQ4] == 0.0 or data_config.ParamReal[REAL_LATSUPQ4] > 5.0:
            logging.warning(f"⚠️ Config\t→\tLat\t→\tLATSUPQ4 deve essere impostato a 1 o leggermente di più")

        _ = {
            "REAL_LATSUPQ0": REAL_LATSUPQ0,
            "REAL_LATSUPQ1": REAL_LATSUPQ1,
            "REAL_LATSUPQ2": REAL_LATSUPQ2,
            "REAL_LATSUPQ3": REAL_LATSUPQ3,
            "REAL_LATSUPQ4": REAL_LATSUPQ4,
        }
        for label, idx in _.items():
            if data_config.ParamRealType[idx] != -1:
                logging.warning(f"⚠️ Config\t→\tLat\t→\t{label.replace('REAL_', '')} deve essere impostato -")

        logging.info("🔍 Fine controllo supporti laterali...")

    def check_oil_temp() -> None:
        logging.info("🔍 Inizio controllo olio...")
        # il numero rappresenta il tipo di dato MISURA_*
        _ = {
            ASSE_REAL_SRTUP: "",
            ASSE_REAL_SRTDOWN: "",
            ASSE_REAL_COEFFUP: "",
            ASSE_REAL_COEFFDOWN: "",
            ASSE_REAL_P1UP: "",
            ASSE_REAL_P1DOWN: "",
            ASSE_REAL_P2UP: "",
            ASSE_REAL_P2DOWN: "",
            ASSE_REAL_SYSPRESSUP1: "",
            ASSE_REAL_SYSPRESSDOWN1: "",
            ASSE_REAL_SYSPRESSUP2: "",
            ASSE_REAL_SYSPRESSDOWN2: "",
            ASSE_REAL_SYSPRESSUP3: "",
            ASSE_REAL_SYSPRESSDOWN3: "",
            ASSE_REAL_BWVMAX: "",
            ASSE_REAL_DSMAXDOWN: -1,
            ASSE_REAL_DSMAXUP: -1,
            ASSE_REAL_FWVMAX: "",
            ASSE_REAL_SMAX: "",
            ASSE_REAL_SMIN: "",
            ASSE_REAL_SSUP: "",
            ASSE_REAL_SINF: "",
            ASSE_REAL_VMINSTARTED: "",
            ASSE_REAL_SHH: "",
            ASSE_REAL_SH: "",
            ASSE_REAL_SL: "",
            ASSE_REAL_SLL: "",
            ASSE_REAL_TILTMAX: -1,
            ASSE_REAL_SLAVEVRESET: "",
            ASSE_REAL_SLAVEVMIN: "",
            ASSE_REAL_MASTERMULT: "",
            ASSE_REAL_MASTERDELTAMIN: "",
            ASSE_REAL_MASTERKSRS: "",
            ASSE_REAL_SLAVEDELTATSTART: "",
            ASSE_REAL_OUTKP: "",
            ASSE_REAL_OUTDELTAT: "",
            ASSE_REAL_SH0: 2,
            ASSE_REAL_SL0: 2,
            ASSE_REAL_TILTMAXDOWN: "",
            ASSE_REAL_FREE_39: "",
            ASSE_REAL_DELTAMOVINGUP: -1,
            ASSE_REAL_DELTAMOVINGDOWN: -1,
            ASSE_REAL_DELTADIV: -1,
            ASSE_REAL_DELTAMOVINGSUPUP: -1,
            ASSE_REAL_DELTAMOVINGINFUP: -1,
            ASSE_REAL_DELTAMOVINGSUPDOWN: -1,
            ASSE_REAL_DELTAMOVINGINFDOWN: -1,
            ASSE_REAL_DELTAAUTO: -1,
            ASSE_REAL_BWACCMAX: "",
            ASSE_REAL_FWACCMAX: "",
            ASSE_REAL_OPTPARAM1: "",
            ASSE_REAL_OPTPARAM2: "",
            ASSE_REAL_OPTPARAM3: "",
            ASSE_REAL_AXISCOUPMIN: "",
            ASSE_REAL_FREE_54: ""
        }
        _to_control_idx = [ASSE_REAL_DSMAXDOWN, ASSE_REAL_DSMAXUP, ASSE_REAL_TILTMAX, ASSE_REAL_SH0, ASSE_REAL_SL0,
                           ASSE_REAL_DELTAMOVINGUP, ASSE_REAL_DELTAMOVINGDOWN, ASSE_REAL_DELTADIV,
                           ASSE_REAL_DELTAMOVINGSUPUP, ASSE_REAL_DELTAMOVINGINFUP,
                           ASSE_REAL_DELTAMOVINGSUPDOWN,ASSE_REAL_DELTAMOVINGINFDOWN,ASSE_REAL_DELTAAUTO]
        diff = False
        if data_config.AxisFunInd[FUN_AXIS_OILTEMP] != -1:
            axisOil = data_config.Axis_Param[data_config.AxisFunInd[FUN_AXIS_OILTEMP]]
            for i, value in _.items():
                #  i == ASSE_REAL_BWVMAX or i == ASSE_REAL_FWVMAX or i == ASSE_REAL_DSMAXUP or i == ASSE_REAL_DSMAXDOWN:
                if i not in _to_control_idx:
                    continue
                if axisOil.typval[i] != value:
                    logging.warning(f'attuale: {axisOil.typval[i]}, invece di :{_[i]}, id: {i}')
                    diff = True
            if diff:
                logging.critical(f"N\ttype: {str(axisOil.typval).replace(' ', '')}")
                newValue = axisOil.typval.copy()
                for i in _.keys():
                    if i in _to_control_idx:
                        newValue[i] = _[i]
                logging.warning(f"Y\ttype: {str(newValue).replace(' ', '')}")
        logging.info("🔍 Fine controllo olio...")

    def check_release() -> None:
        logging.info("🔍 Inizio controllo sgancio...")
        if data_config.AxisFunInd[FUN_AXIS_DE] == -1:
            logging.warning("Indice DE non configurato in Params > Functions")
            return
        if data_config.AxisFunInd[FUN_AXIS_PINCH] == -1:
            logging.warning("Indice B non configurato in Params > Functions")
            return
        pinchName = f"[{data_config.AxisFunInd[FUN_AXIS_PINCH]}]{data_config.Axis_Name[data_config.AxisFunInd[FUN_AXIS_PINCH]] or f'AXIS_{data_config.AxisFunInd[FUN_AXIS_PINCH]}'}"
        safetyDown = [
            ASSE_INT_SAFETYDOWNIND1, ASSE_INT_SAFETYDOWNIND2, ASSE_INT_SAFETYDOWNIND3,
            ASSE_INT_SAFETYDOWNIND4, ASSE_INT_SAFETYDOWNIND5, ASSE_INT_SAFETYDOWNIND6
        ]
        if not any(make_axis_sys_addr(AXIS_GROUPS_ORDER[IO_SYSAXIS_L], data_config.AxisFunInd[FUN_AXIS_PINCH]) == data_config.Axis_Param[data_config.AxisFunInd[FUN_AXIS_DE]].intval[x] for x in safetyDown):
            logging.warning(f"⚠️ {pinchName}.L non è presente negli interlock down direttamente va aggiunto!")
        safetyUp = [
            ASSE_INT_SAFETYUPIND1, ASSE_INT_SAFETYUPIND1, ASSE_INT_SAFETYUPIND1,
            ASSE_INT_SAFETYUPIND1, ASSE_INT_SAFETYUPIND1, ASSE_INT_SAFETYUPIND1
        ]
        if any(make_axis_sys_addr(AXIS_GROUPS_ORDER[IO_SYSAXIS_L], data_config.AxisFunInd[FUN_AXIS_PINCH]) == data_config.Axis_Param[data_config.AxisFunInd[FUN_AXIS_DE]].intval[x] for x in safetyUp):
            logging.warning(f"⚠️ {pinchName}.L è presente negli interlock up va rimosso!")
        # controllo flag
        # controllo quota apertura sgancio
        if data_config.Axis_Param[data_config.AxisFunInd[FUN_AXIS_PINCH]].realval[ASSE_REAL_SHH] <= data_config.Axis_Param[data_config.AxisFunInd[FUN_AXIS_PINCH]].realval[ASSE_REAL_SL]:
            logging.warning(f"⚠️ {pinchName}.HH è minore o uguale a {pinchName}.L quota reset automatico")
        logging.info("🔍 Fine controllo sgancio...")

    def check_safety() -> None:
        logging.info("🔍 Inizio controllo safety...")
        if data_config.ParamInt[INT_HOLDTORUNTYPE] != SAFETY_INT:
            logging.warning("⚠️ Hold to run non impostato su INT")
        for i in range(0, MAX_ASSE):
            axis = data_config.Axis_Param[i]
            axis_name = data_config.Axis_Name[i] or f"AXIS_{i}"
            if axis.intval[ASSE_INT_HOLDTORUNTYPE] == ASSE_HOLDTORUNTYPE_NONE:
                logging.warning(f"⚠️ [{i}]{axis_name} Hold to run non impostato")
        logging.info("🔍 Fine controllo safety...")

    def check_rotation() -> None:
        logging.info("🔍 Inizio controllo rotazione...")
        axisInd = data_config.AxisFunInd[FUN_AXIS_ROT]
        if axisInd != -1:
            axis = data_config.Axis_Param[axisInd]
            axis_name = data_config.Axis_Name[axisInd] or f"AXIS_{axisInd}"
            if axis.realval[ASSE_REAL_SMAX] != 999999:
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SMAX]]['display']} non impostato a +999999.0 ma a {axis.realval[ASSE_REAL_SMAX]}")
            if axis.realval[ASSE_REAL_SHH] > 10000:
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SHH]]['display']} non impostato correttamente, valore troppo alto: {axis.realval[ASSE_REAL_SHH]}")
            for i in [ASSE_REAL_SMIN, ASSE_REAL_SLL]:
                if axis.realval[i] != -999999:
                    logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][i]]['display']} non impostato a -999999.0 ma a {axis.realval[i]}")
            if axis.realval[ASSE_REAL_SH] != 500:
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SH]]['display']} non impostato a 500.0 ma a {axis.realval[ASSE_REAL_SH]}")
            if axis.realval[ASSE_REAL_SL] != -500:
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SL]]['display']} non impostato a -500.0 ma a {axis.realval[ASSE_REAL_SL]}")
        logging.info("🔍 Fine controllo rotazione...")

    def geometry_check() -> None:
        logging.info("🔍 Inizio controllo geometria...")
        model = data_config.ParamString[0][-4:]
        model_width = model[:2] + '00'
        top_roll_diameter = model[2:] + '0'
        try:
            model_width = int(model_width)
        except ValueError:
            logging.warning("Modello non rilevato")
            return

        if model_width > data_config.ParamReal[REAL_WIDTH]:
            logging.warning(f"⚠️ Modello macchina {model}, lunghezza tavola in geometria più piccolo: {data_config.ParamReal[REAL_WIDTH]}")

        try:
            top_roll_diameter = int(top_roll_diameter)
        except ValueError:
            logging.warning("Diametro rullo non rilevato")
            return

        if top_roll_diameter > data_config.ParamReal[REAL_TROUTERDIAM]:
            logging.warning(f"⚠️ Modello macchina {model}, diametro rullo superiore maggiore di quello in geo: {data_config.ParamReal[REAL_TROUTERDIAM]}")
        elif top_roll_diameter < data_config.ParamReal[REAL_TROUTERDIAM]:
            logging.warning(f"⚠️ Modello macchina {model}, diametro rullo superiore minore 1di quello in geo: {data_config.ParamReal[REAL_TROUTERDIAM]}")

        k = data_config.ParamReal[REAL_K]
        alfa = data_config.ParamReal[REAL_TOPANG] * math.pi / 180.0
        b = data_config.ParamReal[REAL_B]
        htot = b / math.tan(alfa)
        h0 = htot - k
        h0 = round(h0, data_config.UM_NDec[MISURA_LUNGH])
        if round(data_config.ParamReal[REAL_H0],data_config.UM_NDec[MISURA_LUNGH]) != h0:
            logging.critical(f"⚠️ Il parametro calcolato H0 in geometria dovrebbe essere {h0} ma è {data_config.ParamReal[REAL_H0]}")
        logging.info("🔍 Fine controllo geometria...")

    def check_axis_speed_master_slave() -> None:
        logging.info("🔍 Inizio controllo velocità master/slave..")
        for i in range(0, MAX_ASSE):
            slaveAxis = data_config.Axis_Param[i]
            slaveAxisName = get_axis_name(i)
            if slaveAxis.boolval[ASSE_BOOL_CONFIG]:
                if slaveAxis.intval[ASSE_INT_MASTER] != -1:
                    masterAxisInd = slaveAxis.intval[ASSE_INT_MASTER]
                    masterAxis = data_config.Axis_Param[masterAxisInd]
                    masterAxisName = get_axis_name(slaveAxis.intval[ASSE_INT_MASTER])
                    _ = [ASSE_REAL_FWVMAX, ASSE_REAL_BWVMAX]
                    for x in _:
                        if int(masterAxis.realval[x]) != int(slaveAxis.realval[x]):
                            logging.warning(f"⚠️ [{i}]{slaveAxisName} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][x]]['display']} diverso da [{masterAxisInd}]{masterAxisName}")
        # TODO: controllare anche che sia 5.0 e 2.0 MAXVEL
        logging.info("🔍 Fine controllo velocità master/slave...")

    def check_de_tilt() -> None:
        logging.info("🔍 Inizio controllo auto tilt...")
        axisTiltInd = data_config.AxisFunInd[FUN_AXIS_TILT]
        axisDeInd = data_config.AxisFunInd[FUN_AXIS_DE]

        if axisTiltInd == -1:
            logging.warning("Indice tilt non configurato in Params > Functions")
            return
        if axisDeInd == -1:
            logging.warning("Indice DE non configurato in Params > Functions")
            return

        axisTilt = data_config.Axis_Param[axisTiltInd]
        axisTilt_name = data_config.Axis_Name[axisTiltInd] or f"AXIS_{axisTiltInd}"
        axisDe = data_config.Axis_Param[axisDeInd]
        axisDe_name = data_config.Axis_Name[axisDeInd] or f"AXIS_{axisDeInd}"
        if axisDe.intval[ASSE_INT_TIMEOUT2] == 0:
            logging.warning(f"⚠️ [{axisDeInd}]{axisDe_name} TIMEOUT MAN non impostato (tempo di inclinazione automatico DE DOWN)")
        if axisTilt.intval[ASSE_INT_TIMEOUT1] != 0:
            logging.warning(f"⚠️ [{axisTiltInd}]{axisTilt_name} ritardo inclinazione in manuale impostato, interferenza con DE DOWN, impostare a 0")
        logging.info("🔍 Fine controllo auto tilt...")

    def check_stop_alarms() -> None:
        logging.info("🔍 Inizio controllo stop allarmi...")
        normalstop = [0, 2, 3, 4, 6, 7, 28, 29, 32, 33, 83]
        safetyStop = [110, 111, 115, 116, 118, 120, 121, 124, 128, 129, 130, 131, 132, 133, 134, 135, 136, 149, 150,
                      151, 152, 153, 154, 155, 156, 157, 158, 159, 184, 186, 187]
        if get_pgsx_version()[1] >= 25:
            safetyStop = [126, 127, 131, 133, 134, 136, 137, 140, 141, 142, 144, 145, 146, 147, 148, 149, 150, 151,
                          152, 165, 166, 167, 168, 169, 170, 171, 172, 174, 175]
        for i in normalstop:
            alarm = data_config.Alarm_Param[i]
            alarmName = data_config.Alarm_Name[i] or f"ALARM_{i}"
            if alarm.intval[ALARM_INT_MODE] != ALARM_STOP:
                logging.warning(f"⚠️ [{i}]{alarmName} non è configurato come STOP")
        for i in safetyStop:
            alarm = data_config.Alarm_Param[i]
            alarmName = data_config.Alarm_Name[i] or f"ALARM_{i}"
            if alarm.intval[ALARM_INT_MODE] != ALARM_SAFETYSTOP:
                logging.warning(f"⚠️ [{i}]{alarmName} non è configurato come SAFETYSTOP")
        logging.info("🔍 Fine controllo stop allarmi...")

    def check_axis_speed() -> None:
        logging.info("🔍 Inizio controllo coerenza velocità asse...")
        for axisInd in range(0, MAX_ASSE):
            axis = data_config.Axis_Param[axisInd]
            axis_name = data_config.Axis_Name[axisInd] or f"AXIS_{axisInd}"
            bwSlow = axis.intval[ASSE_INT_BWVSLOW]
            fwSlow = axis.intval[ASSE_INT_FWVSLOW]
            maxSpeedFw = axis.realval[ASSE_REAL_FWVMAX]
            maxSpeedBw = axis.realval[ASSE_REAL_BWVMAX]
            if bwSlow not in (-49, -50):
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['intval'][Type_AxisParam_Map['_intval'][ASSE_INT_BWVSLOW]]['display']} impostato a {bwSlow} e non -49 o -50")
            if fwSlow not in (49, 50):
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['intval'][Type_AxisParam_Map['_intval'][ASSE_INT_FWVSLOW]]['display']} impostato a {fwSlow} e non +49 o +50")
            if maxSpeedBw > 0.0:
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_BWVMAX]]['display']} impostato a {maxSpeedBw} maggiore di 0.0")
            if maxSpeedFw < 0.0:
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_FWVMAX]]['display']} impostato a {maxSpeedFw} minore di 0.0")
            if axis.boolval[ASSE_BOOL_CONFIG] and (maxSpeedBw == 0.0 or maxSpeedBw == 0.0):
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro velocità massima impostato a 0.0")
            if axis.realval[ASSE_REAL_MASTERMULT] != 5.0:
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_MASTERMULT]]['display']} impostato a {axis.realval[ASSE_REAL_MASTERMULT]} diverso da 5.0")
            if axis.realval[ASSE_REAL_MASTERDELTAMIN] < 2.0:
                logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_MASTERDELTAMIN]]['display']} impostato a {axis.realval[ASSE_REAL_MASTERDELTAMIN]} inferiore a 2.0")
        logging.info("🔍 Fine controllo coerenza velocità asse...")

    def check_archimeter_params() -> None:
        logging.info("🔍 Inizio controllo parametri archimetro...")
        _ = [
            "REAL_ARCHIMETER_L1",
            "REAL_ARCHIMETER_A1",
            "REAL_ARCHIMETER_B1",
            "REAL_ARCHIMETER_C1",
            "REAL_ARCHIMETER_L2",
            "REAL_ARCHIMETER_A2",
            "REAL_ARCHIMETER_B2",
            "REAL_ARCHIMETER_C2",
            "REAL_ARCHIMETER_L3",
            "REAL_ARCHIMETER_A3",
            "REAL_ARCHIMETER_B3",
            "REAL_ARCHIMETER_C3",
        ]
        for idx_name in _:
            try:
                if data_config.ParamRealType[globals()[idx_name]] != -1:
                    logging.warning(f"⚠️ Config\t→\tArchimetro\t→\t{idx_name.replace('REAL_', '')} deve essere impostato -")
            except KeyError:
                logging.debug(f"⚠️ Impossibile controllare il parametro {idx_name}, chiave non trovata") # TODO: gestire meglio
        logging.info("🔍 Fine controllo parametri archimetro.")

    def check_bypass_unused() -> None:
        logging.info("🔍 Inizio controllo bypass unused...")

        # Indici dei BOOL di bypass negli assi
        axis_bypass_flags = [
            ASSE_BOOL_BP1, ASSE_BOOL_BP2, ASSE_BOOL_BP3, ASSE_BOOL_BP4,
            ASSE_BOOL_BP5, ASSE_BOOL_BP6, ASSE_BOOL_BP7, ASSE_BOOL_BP8,
            ASSE_BOOL_BP9, ASSE_BOOL_BP10, ASSE_BOOL_BP11, ASSE_BOOL_BP12,
        ]

        # Indici ParamInt corrispondenti ai bypass
        outIndBypass = [
            data_config.OutInd[BOOL_IND_BP1],
            data_config.OutInd[BOOL_IND_BP2],
            data_config.OutInd[BOOL_IND_BP3],
            data_config.OutInd[BOOL_IND_BP4],
            data_config.OutInd[BOOL_IND_BP5],
            data_config.OutInd[BOOL_IND_BP6],
            data_config.OutInd[BOOL_IND_BP7],
            data_config.OutInd[BOOL_IND_BP8],
            data_config.OutInd[BOOL_IND_BP9],
            data_config.OutInd[BOOL_IND_BP10],
            data_config.OutInd[BOOL_IND_BP11],
            data_config.OutInd[BOOL_IND_BP12],
        ]

        for bp_idx, bypassOutInd in enumerate(outIndBypass):

            # Se il bypass non è mappato
            if bypassOutInd == -1:

                # Allora cerchiamo chi cazzo lo sta usando lo stesso
                for axisInd in range(MAX_ASSE):
                    axis = data_config.Axis_Param[axisInd]

                    # Nome asse safe
                    raw_name = data_config.Axis_Name[axisInd]
                    axis_name = raw_name.strip() if isinstance(raw_name, str) else f"AXIS_{axisInd}"

                    # Se l'asse ha il flag del bypass → warning
                    if axis.boolval[axis_bypass_flags[bp_idx]]:
                        logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il bypass {Type_AxisParam_Map['boolval'][Type_AxisParam_Map['_boolval'][axis_bypass_flags[bp_idx]]]['display']} attivo ma non è stato mappato")

        logging.info("🔍 Fine controllo bypass unused...")

    def check_remote_control():
        logging.info("🔍 Inizio controllo remote control...")
        count = 0
        REMOTE_RANGES_MED = [
            range(2009, 2013),  # 2009, 2010, 2011, 2012 small
            range(2030, 2031),  # solo 2030
        ]

        REMOTE_RANGES_BIG = [
            range(2009, 2016),  # 2009–2015
            range(2030, 2031),  # solo 2030
        ]
        for diParam in data_config.IO_DI_List:
            if diParam.intval[IO_INT_ADDRTYPE] == IO_TYPE_PNET:
                addr1 = diParam.intval[IO_INT_ADDR1]
                for addr1 in REMOTE_RANGES_BIG or addr1 in REMOTE_RANGES_BIG:
                    count += 1

        isNewRemoteControl = count >= 6
        if isNewRemoteControl:
            logging.info('Rilevati più di 6 I/O di remote control, configurazione nuova')
            if not data_config.ParamBool[BOOL_NEWCONSOLE]:
                logging.warning(f"⚠️ {Config_Map['ParamBool'][Config_Map['_ParamBool'][BOOL_NEWCONSOLE]]['origin'].format(Config_Map['ParamBool'][Config_Map['_ParamBool'][BOOL_NEWCONSOLE]]['display'])} deve essere impostato a True")

            # asse -> (type,row,col,ntot,ndec,rowimp,colimp,ntotimp,ndecimp)
            expected_map: dict[int, tuple[int, int, int, int, int, int, int, int, int]] = {
                0: (0, 1, 19, 6, 1, 1, 19, 6, 3),
                2: (0, 1, 1, 6, 0, 1, 1, 6, 2),
                16: ([-1, 1], -1, -1, -1, -1, -1, -1, -1, -1),
                1: (0, 1, 7, 6, 1, 1, 7, 6, 3),
                17: ([-1, 1], -1, -1, -1, -1, -1, -1, -1, -1),
                3: (0, 1, 13, 6, 1, 1, 13, 6, 3),
                19: ([-1, 1], -1, -1, -1, -1, -1, -1, -1, -1),
            }

            # indici degli int da controllare (stessi usati in Axis_Param[intval])
            label_indices = [
                ASSE_INT_LABELTYPE,
                ASSE_INT_LABELROW,
                ASSE_INT_LABELCOL,
                ASSE_INT_LABELNTOT,
                ASSE_INT_LABELNDEC,
                ASSE_INT_LABELROWIMP,
                ASSE_INT_LABELCOLIMP,
                ASSE_INT_LABELNTOTIMP,
                ASSE_INT_LABELNDECIMP,
            ]

            for axisInd, expected_tuple in expected_map.items():
                if axisInd >= MAX_ASSE:
                    logging.warning(f"[{axisInd}] AXIS_OUT_OF_RANGE: MAX_ASSE={MAX_ASSE}")
                    continue

                axis = data_config.Axis_Param[axisInd]
                axis_name = data_config.Axis_Name[axisInd] or f"AXIS_{axisInd}"

                for label_idx, expected_value in zip(label_indices, expected_tuple):
                    display = Type_AxisParam_Map["intval"][Type_AxisParam_Map["_intval"][label_idx]]["display"]
                    origin = Type_AxisParam_Map["intval"][Type_AxisParam_Map["_intval"][label_idx]]["origin"]

                    current_value = axis.intval[label_idx]
                    if isinstance(expected_value, list):
                        if current_value not in expected_value:
                            logging.warning(f"{origin.format(axisInd, axis_name)} ha il valore {display} impostato a {current_value} invece che uno tra {expected_value}")
                    else:
                        if current_value != expected_value:
                            logging.warning(f"{origin.format(axisInd, axis_name)} ha il valore {display} impostato a {current_value} invece che {expected_value}")

        logging.info("🔍 Fine controllo remote control...")

    def check_axis_sp() -> None:
        logging.info("🔍 Inizio controllo SP...")
        for axisInd in range(0, MAX_ASSE):
            axis = data_config.Axis_Param[axisInd]
            axis_name = data_config.Axis_Name[axisInd] or f"AXIS_{axisInd}"
            for val in [ASSE_INT_P1, ASSE_INT_P2]:
                if axis.intval[val] != -1:
                    logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['intval'][Type_AxisParam_Map['_intval'][val]]['display']} impostato a {axis.intval[val]}")
        logging.info("🔍 Fine controllo SP...")

    def check_feedback_ratios() -> None:
        logging.info("🔍 Inizio controllo rapporti feedback...")
        for axisInd in range(0, MAX_ASSE):
            axis = data_config.Axis_Param[axisInd]
            axis_name = data_config.Axis_Name[axisInd] or f"AXIS_{axisInd}"
            if axis.intval[ASSE_INT_FEEDBACK] != -1:
                feedback = data_config.Feedback_Param[axis.intval[ASSE_INT_FEEDBACK]]
                if feedback.realval[FB_REAL_RATIO] != 1:
                    logging.warning(f"⚠️ [{axisInd}]{axis_name} sta usando il feedback {axis.intval[ASSE_INT_FEEDBACK]} con ratio: {feedback.realval[FB_REAL_RATIO]}")

        logging.info("🔍 Fine controllo rapporti feedback...")

    def check_tilt_max_lateral() -> None:
        ...

    def check_interlock_alarm_sys_addr():
        logging.info("🔍 Inizio controllo allarmi con indirizzi di sistema...")
        pinchingPS = 97
        pinchingPS_IO = [get_sys_addr("ALARM.VAL", 97), get_sys_addr("ALARM.VAL", 165),
                         get_sys_addr("ALARM.VAL", 100), get_sys_addr("ALARM.VAL", 101),
                         get_sys_addr("ALARM.VAL", 167), get_sys_addr("ALARM.VAL", 168),
                         get_sys_addr("ALARM.VAL", 98), get_sys_addr("ALARM.VAL", 166)]
        major, minor, patch, build = get_pgsx_version()
        if patch >= 50:  # passando alla versione 50 si aggiungono 16 allarmi in piu in mezzo e quindi cambiano gli indirizzi di sistema, bisogna tenerne conto per il controllo
            pinchingPS = 113
            pinchingPS_IO = [get_sys_addr("ALARM.VAL", 97+16), get_sys_addr("ALARM.VAL", 165+16),
                             get_sys_addr("ALARM.VAL", 100+16), get_sys_addr("ALARM.VAL", 101+16),
                             get_sys_addr("ALARM.VAL", 167+16), get_sys_addr("ALARM.VAL", 168+16),
                             get_sys_addr("ALARM.VAL", 98+16), get_sys_addr("ALARM.VAL", 166+16)]
        alarmPinching_IN = data_config.Alarm_Param[pinchingPS].intval[ALARM_INT_INDIN]
        # if alarmPinching_IN != -1:
        #     exprGroup = get_expr_from_di(alarmPinching_IN)
        #     if exprGroup:
        #         for index, data in enumerate(exprGroup):
        #             if data[1] == -1:
        #                 continue
        #             if data[1] not in pinchingPS_IO:
        #                 logging.warning(f"⚠️ Alarm Pinching usa un indirizzo IO di sistema {data[1]} errato")
        # TODO: verificare se questo allarme è usato in safety interlock o altrove
        # todo: per ogni asse tipo rotazione o rullo, guardo i safety interlock down e vedo se c è qualche allarme, se c è un tipo calcolato guardo se ha espressioni che usano indirizzi di sistema e se sono quelli giusti, se invece è un allarme normale guardo se è usato in qualche interlock o altrove e se usa indirizzi di sistema guardo se sono quelli giusti
        axis_to_check = [FUN_AXIS_ROT, FUN_AXIS_PRE, FUN_AXIS_BEND, FUN_AXIS_PINCH]
        for axisFun in axis_to_check:
            if data_config.AxisFunInd[axisFun] != -1:
                axis = data_config.Axis_Param[data_config.AxisFunInd[axisFun]]
                axis_name = data_config.Axis_Name[data_config.AxisFunInd[axisFun]] or f"AXIS_{data_config.AxisFunInd[axisFun]}"
                safetyDown = [
                    ASSE_INT_SAFETYDOWNIND1, ASSE_INT_SAFETYDOWNIND2, ASSE_INT_SAFETYDOWNIND3,
                    ASSE_INT_SAFETYDOWNIND4, ASSE_INT_SAFETYDOWNIND5, ASSE_INT_SAFETYDOWNIND6
                ]
                to_check = {addr: False for addr in pinchingPS_IO}

                def _docheck(DI: int):
                    safetyDownInput = data_config.IO_DI_List[DI]
                    if safetyDownInput.intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
                        exprGroup = get_expr_from_di(DI)
                        if exprGroup:
                            for index, data in enumerate(exprGroup):
                                if data[1] == -1:
                                    continue
                                if data[1] in to_check:
                                    to_check[data[1]] = True

                for x in safetyDown:
                    safetyDownAddress = axis.intval[x]
                    if safetyDownAddress != -1:
                        is_system = decode_sys_addr_name(safetyDownAddress)
                        if is_system:
                            if safetyDownAddress in to_check:
                                to_check[safetyDownAddress] = True
                        else:
                            _docheck(safetyDownAddress)

                if any(not used for used in to_check.values()):
                    logging.warning(f"⚠️ [{data_config.AxisFunInd[axisFun]}]{axis_name} ha allarmi di safety down che usano indirizzi di sistema ma non tutti quelli necessari, indirizzi mancanti: {', '.join([str(decode_sys_addr_name(addr)) + ' =' + str(addr) for addr, used in to_check.items() if not used])}")

        # TODO: forse è meglio print degli allarmi che sono usati in giro;
        logging.info("🔍 Fine controllo allarmi con indirizzi di sistema...")

    def check_all_sys_alarms() -> None:
        logging.info("🔍 Inizio controllo totale allarmi con indirizzi di sistema...")
        for alarmInd in range(MAX_ALARM):
            alarmName = data_config.Alarm_Name[alarmInd] or f"ALARM_{alarmInd}"
            idx = get_sys_addr("ALARM.VAL", alarmInd)
            result = run_io_search(IO_DI, idx, verbose=True)
            if result:
                logging.warning(f"⚠️ [{alarmInd}]{alarmName} è un allarme con indirizzo di sistema {idx}, usato da: {', '.join(result)}")
        logging.info("🔍 Fine controllo totale allarmi con indirizzi di sistema...")

    def seq_check() -> None:
        logging.info("🔍 Inizio controllo sequenze...")
        for idx, Input in enumerate(data_config.Input_Param):
            seq = Input.intval[INPUT_INT_SEQID]
            if seq != -1:
                logging.warning(f"⚠️ L'input {idx} ha la sequenza impostata su {seq}" + f"{Type_SeqLabel.get(seq, '')}")
        logging.info("🔍 Fine controllo sequenze...")

    def deadband_feedback_check() -> None:
        logging.info("🔍 Inizio controllo deadband feedback...")
        for axisInd in range(0, MAX_ASSE):
            axis = data_config.Axis_Param[axisInd]
            axis_name = data_config.Axis_Name[axisInd] or f"AXIS_{axisInd}"
            if axis.intval[ASSE_INT_FEEDBACK] != -1:
                feedback = data_config.Feedback_Param[axis.intval[ASSE_INT_FEEDBACK]]
                if feedback.realval[FB_REAL_DEADBAND] == 0:
                    logging.warning(f"⚠️ [{axisInd}]{axis_name} sta usando il feedback {axis.intval[ASSE_INT_FEEDBACK]} con deadband: uguale a 0.0")
        logging.info("🔍 Fine controllo deadband feedback...")

    def check_automatic_params() -> None:
        """
        Controlla che il parametro HH non sia troppo lontano dal MAX
        todo: se resettype  = 3 quota reset H solo per laterale
        Returns:
        """
        logging.info("🔍 Inizio controllo parametri automatici...")
        to_check = [FUN_AXIS_PRE, FUN_AXIS_BEND]
        for funInd in to_check:
            axisInd = data_config.AxisFunInd[funInd]
            if axisInd != -1:
                axis = data_config.Axis_Param[axisInd]
                axis_name = data_config.Axis_Name[axisInd] or f"AXIS_{axisInd}"
                if axis.realval[ASSE_REAL_SHH] > axis.realval[ASSE_REAL_SMAX]:
                    logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SHH]]['display']} ({axis.realval[ASSE_REAL_SHH]}) maggiore di {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SMAX]]['display']} ({axis.realval[ASSE_REAL_SMAX]})")
                elif axis.realval[ASSE_REAL_SMAX] - 10.0 > axis.realval[ASSE_REAL_SHH]:
                    logging.warning(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SHH]]['display']} ({axis.realval[ASSE_REAL_SHH]})troppo lontano da {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SMAX]]['display']} ({ axis.realval[ASSE_REAL_SMAX]}), considerare di aumentare {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SHH]]['display']} o aumentare {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SMAX]]['display']}")
        logging.info("🔍 Fine controllo parametri automatici...")

    def check_params_um() -> None:
        logging.info("🔍 Inizio controllo unità di misura parametri...")
        _ = {
            MISURA_LUNGH: [],
            MISURA_GRAD: [],
            MISURA_AREA: [],
            -1: []  # per parametri che non dovrebbero avere unità di misura o non è possibile stabilirla a priori
        }
        _[-1].extend([REAL_TOPANG])  # parametro che potrebbe essere in gradi o in radianti a seconda della configurazione, va controllato a parte
        _[MISURA_LUNGH].extend([REAL_WIDTH, REAL_B, REAL_K, REAL_H0, REAL_TRDIAM, REAL_LRDIAM, REAL_SRDIAM,
                                REAL_STARTSENSX, REAL_STARTSENSZ, REAL_STARTSENSORDIST, REAL_EXTDIST, REAL_LREFFCYLAREA,
                                REAL_D, REAL_E, REAL_F, REAL_G, REAL_S, REAL_TROUTERDIAM, REAL_LROUTERDIAM,
                                REAL_SROUTERDIAM, REAL_DAES, REAL_B2ANG])  # Pagina Geo
        _[MISURA_GRAD].extend([
            REAL_LATSUPR0, REAL_LATSUPR1, REAL_LATSUPR2, REAL_LATSUPR3, REAL_LATSUPR4,
            REAL_LATSUPQ0, REAL_LATSUPQ1, REAL_LATSUPQ2, REAL_LATSUPQ3, REAL_LATSUPQ4
        ])  # Pagina supporto laterale
        _[MISURA_LUNGH].extend([
            REAL_ALIGN_CENTDIST1, REAL_ALIGN_CENTDIST2, REAL_ALIGN_CENTDIST3, REAL_ALIGN_DELTACENTPOS,
        ])  # Pagina RT
        _[MISURA_LUNGH].extend([REAL_LSX, REAL_LSY, REAL_LSL, REAL_LST, REAL_TSTX]) # parametri per supporto orizzontale
        _[MISURA_AREA].extend([REAL_LREFFCYLAREA])

        for _misura, _groups in _.items():
            for paramId in _groups:
                if data_config.ParamRealType[paramId] != _misura:
                    txt = (f"⚠️ {Config_Map['_ParamRealType'][paramId]} "
                           f"ha unità di misura {Unita_Misura[data_config.ParamRealType[paramId]]} "
                           f"invece di {Unita_Misura[_misura]}")
                    logging.warning(txt)

        logging.info("🔍 Fine controllo unità di misura parametri...")

    def motor_checks() -> None:
        logging.info("🔍 Inizio controllo motori...")
        # TODO: notificare se le termiche sono state inserite nei motori (no resistanza)
        # TODO: verificare che se motore in seq ce ne siano altri in seq (se sono disattivati fa cose strane tipop va giu e su)

        for i in range(0, MAX_MOTORE):
            motorEnabled = data_config.Motor_Config[i]
            if motorEnabled:
                # controllo termiche
                if data_config.Motor_TRInd[i] == -1:
                    logging.warning(f"⚠️ Motore [{i}]: termica non presente")

        # verifica sequenza motori
        seqEnabled = any(data_config.Motor[i].seq and data_config.Motor_Config[i] for i in range(MAX_MOTORE))

        if seqEnabled:
            for i in range(MAX_MOTORE):
                if data_config.Motor[i].seq and not data_config.Motor_Config[i]:
                    logging.warning(f"⚠️ Motore [{i}] è in sequenza ma non è abilitato")

            # controllo che non ci sia un seq abilitato senza primario abilitato
            if not data_config.Motor[0].seq:
                logging.warning("⚠️ Sequenza motori abilitata ma motore primario [0] non abilitato")

            # todo: gathering del motore principale in automatico
            # controllo che timeoutbtn sia > 0 se è in sequenza e che copri tutta la sequenza
            if data_config.Motor[0].seq:
                maxTimer = 0
                for i in range(MAX_MOTORE):
                    if data_config.Motor[i].seq:
                        maxTimer += data_config.Motor[i].timeout
                diff = maxTimer - data_config.Motor[0].timeoutbtn
                if data_config.Motor[0].timeoutbtn < maxTimer:
                    logging.warning(f"⚠️ Motore [0] ha timeoutbtn troppo basso per la sequenza configurata, considerare di aumentarlo a almeno {diff * 100} ms")

        for i in range(MAX_MOTORE):
            if data_config.Motor_Config[i] and data_config.Motor[i].timeout != 0 and not data_config.Motor[i].seq:
                logging.warning(f"⚠️ Motore [{i}] ha un ritardo allo spegnimento di {data_config.Motor[i].timeout} s")

        logging.info("🔍 Fine controllo motori...")

    def check_ri_bug() -> None:
        # TODO: cerifica bug RI vedere se tutti i campi o la maggiorpare di Enabled è diverso da -1
        logging.info("🔍 Inizio controllo bug RI...")
        for i in range(0, MAX_RI):
            if data_config.IO_RI_List[i].intval[IO_INT_NBYTES] == 0 and data_config.IO_RI_List[i].intval[IO_INT_TIMEOUT] == 0 and data_config.IO_RI_List[i].intval[IO_INT_ININD] == 0:
                logging.warning(f"⚠️ RI [{i}] potenzialmente non configurato, ha indirizzo di input 0, timeout 0 e nbytes 0, verificare che non sia un RI inutilizzato o configurato erroneamente")
        logging.info("🔍 Fine controllo bug RI...")

    def check_io_calc() -> None:
        for idx, IO in enumerate(data_config.IO_DI_List):
            if IO.intval[IO_INT_ADDRTYPE] != IO_TYPE_CALC:
                exprGroup = get_expr_from_di(idx)
                if exprGroup:
                    for index, data in enumerate(exprGroup):
                        if data[1] == -1:
                            continue
                        else:
                            logging.warning(f"⚠️ DI {idx} ha espressioni calcolate ma non è un tipo CALC")

    def check_axis_bypass() -> None:
        logging.info("🔍 Inizio controllo bypass assi...")

        # Costruzione dinamica BP1..BP12 usando le costanti esistenti
        bypass_map: list[tuple[int, int, int]] = []

        for bp_num in range(1, MAX_BYPASS + 1):
            axis_bool_name = f"ASSE_BOOL_BP{bp_num}"
            out_ind_name = f"BOOL_IND_BP{bp_num}"

            if axis_bool_name not in globals() or out_ind_name not in globals():
                continue

            bypass_map.append((
                bp_num,
                globals()[axis_bool_name],  # es. ASSE_BOOL_BP1
                globals()[out_ind_name],  # es. BOOL_IND_BP1
            ))

        groups: dict[tuple[int, ...], list[str]] = {}

        for axisInd in range(0, MAX_ASSE):
            axis = data_config.Axis_Param[axisInd]

            axis_name = get_axis_name(axisInd)

            active_bp: list[int] = []

            for bp_num, axis_bool_idx, out_ind_idx in bypass_map:
                if axis_bool_idx >= len(axis.boolval):
                    continue

                if axis.boolval[axis_bool_idx]:
                    active_bp.append(bp_num)

                    # controllo bypass attivo ma non mappato
                    try:
                        if data_config.OutInd[out_ind_idx] == -1:
                            logging.warning(f"⚠️ [{axisInd}]{axis_name} ha BP{bp_num} attivo ma non è stato mappato")
                    except Exception:
                        logging.warning(f"⚠️ [{axisInd}]{axis_name} ha BP{bp_num} attivo ma controllo mappatura non riuscito")

            if active_bp:
                key = tuple(active_bp)
                groups.setdefault(key, []).append(f"[{axisInd}]{axis_name}")

        # Print finale tipo:
        # BP1 (name):
        # asse1
        #
        # BP1+BP2 (name+name):
        # asse2
        for key in sorted(groups.keys()):
            bp_labels: list[str] = []
            bp_names: list[str] = []

            for bp_num in key:
                out_ind_name = f"BOOL_IND_BP{bp_num}"
                out_ind_idx = globals().get(out_ind_name)

                bp_labels.append(f"BP{bp_num}")

                bp_name = None
                if out_ind_idx is not None:
                    try:
                        do_ind = data_config.OutInd[out_ind_idx]
                        if do_ind != -1:
                            bp_name = get_io_name(iotype=IO_DO, Ind=do_ind)
                    except Exception:
                        bp_name = None

                if bp_name:
                    bp_names.append(bp_name)

            header = "+".join(bp_labels)

            if bp_names:
                header += f" ({' + '.join(bp_names)})"

            logging.warning(f"\n{header}:")
            for axis_name in groups[key]:
                logging.warning(axis_name)

        logging.info("🔍 Fine controllo bypass assi.")

    def check_axis_slaves() -> None:
        logging.info("🔍 Inizio controllo assi master/slave...")

        real_params_to_check = [
            ASSE_REAL_FWVMAX,
            ASSE_REAL_BWVMAX,
        ]

        bypass_params_to_check = [
            ASSE_BOOL_BP1,
            ASSE_BOOL_BP2,
            ASSE_BOOL_BP3,
            ASSE_BOOL_BP4,
            ASSE_BOOL_BP5,
            ASSE_BOOL_BP6,
            ASSE_BOOL_BP7,
            ASSE_BOOL_BP8,
            ASSE_BOOL_BP9,
            ASSE_BOOL_BP10,
            ASSE_BOOL_BP11,
            ASSE_BOOL_BP12,
        ]

        def get_axis_chain(axis_ind: int) -> tuple[list[int], bool]:
            """
            Ritorna la catena slave -> master -> master del master...
            Esempio: 43 -> 42 -> 2

            Il bool indica se la catena è valida.
            """
            chain = []
            visited_axes = set()

            current_axis_ind = axis_ind

            while True:
                if current_axis_ind in visited_axes:
                    chain.append(current_axis_ind)
                    return chain, False

                if current_axis_ind < 0 or current_axis_ind >= MAX_ASSE:
                    chain.append(current_axis_ind)
                    return chain, False

                visited_axes.add(current_axis_ind)
                chain.append(current_axis_ind)

                current_axis = data_config.Axis_Param[current_axis_ind]
                master_axis_ind = current_axis.intval[ASSE_INT_MASTER]

                if master_axis_ind == -1:
                    return chain, True

                current_axis_ind = master_axis_ind

        for slave_axis_ind in range(0, MAX_ASSE):
            slave_axis = data_config.Axis_Param[slave_axis_ind]

            # Controlla solo assi configurati
            if not slave_axis.boolval[ASSE_BOOL_CONFIG]:
                continue

            # Se non ha master, non è uno slave
            if slave_axis.intval[ASSE_INT_MASTER] == -1:
                continue

            axis_chain, valid_chain = get_axis_chain(slave_axis_ind)
            axis_chain_str = " -> ".join(str(axis_ind) for axis_ind in axis_chain)

            if not valid_chain:
                logging.warning(
                    f"⚠️ {axis_chain_str}   (catena master/slave non valida)"
                )
                continue

            master_axis_ind = axis_chain[-1]
            master_axis = data_config.Axis_Param[master_axis_ind]

            if not master_axis.boolval[ASSE_BOOL_CONFIG]:
                logging.warning(
                    f"⚠️ {axis_chain_str}   (master non configurato)"
                )
                continue

            # Controllo velocità massime slave/root-master
            for real_idx in real_params_to_check:
                real_label = Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][real_idx]]['display']

                slave_value = slave_axis.realval[real_idx]
                master_value = master_axis.realval[real_idx]

                if not math.isclose(slave_value, master_value, rel_tol=0.0, abs_tol=1e-9):
                    logging.warning(
                        f"⚠️ {axis_chain_str}   ({real_label}  {slave_value} != {master_value})"
                    )

            # Controllo bypass attivi slave/root-master
            for bool_idx in bypass_params_to_check:
                bool_label = Type_AxisParam_Map['boolval'][Type_AxisParam_Map['_boolval'][bool_idx]]['display']

                slave_bypass_active = slave_axis.boolval[bool_idx]
                master_bypass_active = master_axis.boolval[bool_idx]

                if slave_bypass_active != master_bypass_active:
                    logging.warning(
                        f"⚠️ {axis_chain_str}   ({bool_label}  {slave_bypass_active} != {master_bypass_active})"
                    )

        logging.info("🔍 Fine controllo assi master/slave...")

    def check_default_axis_speed() -> None:
        logging.info("🔍 Inizio controllo velocità di default...")
        for i in range(0, MAX_ASSE):
            defaultSpeed = data_config.Axis_Param[i].intval[ASSE_INT_DEFSPEED]
            maxVelPerc = data_config.Axis_Param[i].intval[ASSE_INT_MAXVELPERC]
            delayUp = data_config.Axis_Param[i].intval[ASSE_INT_DELAYUP]
            delayDown = data_config.Axis_Param[i].intval[ASSE_INT_DELAYDOWN]
            if defaultSpeed not in [100]:
                logging.warning(f"⚠️ {get_axis_fullname(i)} ha il parametro {Type_AxisParam_Map['intval'][Type_AxisParam_Map['_intval'][ASSE_INT_DEFSPEED]]['display']} impostato a {defaultSpeed} invece di 100")
            if maxVelPerc not in [100]:
                logging.warning(f"⚠️ {get_axis_fullname(i)} ha il parametro {Type_AxisParam_Map['intval'][Type_AxisParam_Map['_intval'][ASSE_INT_MAXVELPERC]]['display']} impostato a {maxVelPerc} invece di 100")
            if delayUp != 0:
                logging.warning(f"⚠️ {get_axis_fullname(i)} ha il parametro {Type_AxisParam_Map['intval'][Type_AxisParam_Map['_intval'][ASSE_INT_DELAYUP]]['display']} impostato a {delayUp} invece di 100")
            if delayDown != 0:
                logging.warning(f"⚠️ {get_axis_fullname(i)} ha il parametro {Type_AxisParam_Map['intval'][Type_AxisParam_Map['_intval'][ASSE_INT_DELAYDOWN]]['display']} impostato a {delayDown} invece di 100")

    def check_shock_absorber() -> None:
        logging.info("🔍 Inizio controllo shock absorber (BP12)...")
        used = any(data_config.Axis_Param[i].boolval[ASSE_BOOL_BP12] for i in range(0, MAX_ASSE))
        if used:
            disableOnRotation = data_config.InInd[BOOL_IND_DISABLEBP12]
            if disableOnRotation == -1:
                logging.warning(f"⚠️ Il bypass shock absorber (BP12) è usato da almeno un asse ma non è definito in: '{Config_Map['OutInd']['BOOL_IND_DISABLEBP12']['origin']}'")
            else:
                isSW = data_config.IO_DI_List[data_config.InInd[BOOL_IND_DISABLEBP12]].intval[IO_INT_ADDRTYPE] == IO_TYPE_SW
                ioAddress = data_config.IO_DI_List[data_config.InInd[BOOL_IND_DISABLEBP12]].intval[IO_INT_ADDR1]
                if not isSW and ioAddress != 12:
                    logging.warning(f"⚠️ Il bypass shock absorber (BP12) è non viene disabilitato da SW con indirizzo 12, attualmente è usato {get_io_fullname(iotype=IO_DI, Ind=data_config.InInd[BOOL_IND_DISABLEBP12])}")
        logging.info("🔍 Fine controllo shock absorber (BP12)...")


    foo = [check_axis_flag, check_duplicate_do_ao_usage, check_duplicate_obj_usage, clean_di_axis_check, duplicate_io_address,
           check_axis_um, check_duplicate_funaxis, check_lat_sup, check_oil_temp, check_release, check_safety, check_rotation,
           geometry_check, check_axis_speed_master_slave, check_forbidden_ao_do_usage, check_de_tilt, check_stop_alarms, check_axis_speed,
           check_archimeter_params, check_bypass_unused, check_remote_control, check_feedback_ratios, check_axis_sp, check_tilt_max_lateral,
           check_interlock_alarm_sys_addr, seq_check, check_automatic_params, deadband_feedback_check,
           check_all_sys_alarms, check_params_um, motor_checks, check_ri_bug, check_io_calc, check_axis_bypass, check_axis_slaves, check_default_axis_speed,
           check_shock_absorber]

    for func in foo:
        logging.info('-' * 60)
        func()
    logger.debug("OUT: custom_function")


if __name__ == "__main__":
    populate_from_yaml_file("../../config.yaml")
    custom_function()
