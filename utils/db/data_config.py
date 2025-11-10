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
import os
import sys

from pathlib import Path
from typing import Any, List, Dict, Sequence, Optional

from utils.exports.tia_constants_map import *
from utils.yaml.data.core import make_axis_sys_addr
from utils.yaml.data.costants import BASE_AXIS, AXIS_GROUP_STEP, ALARM_GROUP_STEP, AXIS_GROUPS_ORDER
from utils.yaml.load import load_yaml
from utils.exports.tia_constants import *  # noqa: F401,F403  (porta DATA_CONFIG, MAX_*, costanti simboliche, UDT, ecc.)

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
        logging.INFO: RESET,        # INFO resta normale
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
handler.setFormatter(ColorFormatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))

log_level = logging.DEBUG if os.path.exists("debug.yaml") else logging.INFO


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

data_config.IO_DI_List = []
data_config.IO_DO_List = []
data_config.IO_AI_List = []
data_config.IO_AO_List = []
data_config.IO_RI_List = []


# ------------------------------
# Public API
# ------------------------------
def populate_from_yaml_file(yaml_path: Path | str) -> None:
    p = Path(yaml_path).resolve()
    data = load_yaml(str(p))
    if not isinstance(data, dict):
        raise ValueError("Il YAML deve essere un dict.")
    deserialize_config(data)


def deserialize_config(data: Dict[str, Any]) -> None:
    logger.debug('IN: deserialize_config')
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


# ------------------------------
# Header / Card / AxInd
# ------------------------------
def _deserialize_header(data: Dict[str, Any]) -> None:
    """ header / pstring / pbool / pint / preal / ptype — compatibile con YAML dove 'param' è lista di dizionari """
    header = _as_list(data.get("header"))
    logger.debug(f"header: {header}")

    # Prepara Config_Header
    max_len = getattr(data_config, "MAX_HEADER", len(header))
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
    max_len = getattr(data_config, "MAX_PARAMSTRING", len(pstring))
    if len(data_config.ParamString) <= max_len:
        data_config.ParamString = [""] * (max_len + 1)
    for i in range(max_len + 1):
        data_config.ParamString[i] = str(pstring[i]) if i < len(pstring) else ""

    # --- pbool ---
    max_len = getattr(data_config, "MAX_PARAMBOOL", len(pbool))
    if len(data_config.ParamBool) <= max_len:
        data_config.ParamBool = [False] * (max_len + 1)
    for i in range(max_len + 1):
        data_config.ParamBool[i] = _bool_from_int(pbool[i]) if i < len(pbool) else False

    # --- pint ---
    max_len = getattr(data_config, "MAX_PARAMINT", len(pint))
    if len(data_config.ParamInt) <= max_len:
        data_config.ParamInt = [0] * (max_len + 1)
    for i in range(max_len + 1):
        data_config.ParamInt[i] = _to_int(pint[i]) if i < len(pint) else 0

    # --- preal ---
    max_len = getattr(data_config, "MAX_PARAMREAL", len(preal))
    if len(data_config.ParamReal) <= max_len:
        data_config.ParamReal = [0.0] * (max_len + 1)
        data_config.ParamRealCfg = [0.0] * (max_len + 1)
    for i in range(max_len + 1):
        val = _to_float(preal[i]) if i < len(preal) else 0.0
        data_config.ParamRealCfg[i] = val
        data_config.ParamReal[i] = val

    # --- ptype ---
    max_len = getattr(data_config, "MAX_PARAMREAL", len(ptype))
    if len(data_config.ParamRealType) <= max_len:
        data_config.ParamRealType = [-1] * (max_len + 1)
    for i in range(max_len + 1):
        data_config.ParamRealType[i] = _to_int(ptype[i], -1) if i < len(ptype) else -1


def _deserialize_card_exc(data: Dict[str, Any]) -> None:
    """ card / exc → struttura SDO se presente """
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


def _deserialize_axind_in_out(data: Dict[str, Any]) -> None:
    """ axind / in / out """
    axind = _as_list(data.get("axind"))
    limit = min(len(data_config.AxisFunInd), getattr(data_config, "MAX_ASSEFUNIND", len(axind)) + 1)
    for i in range(limit):
        data_config.AxisFunInd[i] = _to_int(axind[i]) if i < len(axind) else -1

    in_list = _as_list(data.get("in"))
    limit = min(len(data_config.InInd), getattr(data_config, "MAX_STATOBOOL", len(in_list)) + 1)
    for i in range(limit):
        data_config.InInd[i] = _to_int(in_list[i], -1) if i < len(in_list) else -1

    out_list = _as_list(data.get("out"))
    limit = min(len(data_config.OutInd), getattr(data_config, "MAX_STATOBOOL", len(out_list)) + 1)
    for i in range(limit):
        data_config.OutInd[i] = _to_int(out_list[i], -1) if i < len(out_list) else -1


# ------------------ IO (di/ai/do/ao/ri) ------------------
def _deserialize_io(data: Dict[str, Any]) -> None:
    # data['io'] è un dict: {'di': [[...], ...], 'ai': [...], ...}
    io_data = data.get("io", {})
    for field in ("di", "ai", "do", "ao", "ri"):
        rows = _as_list(io_data.get(field))
        for ind, row in enumerate(rows):
            if row is None:
                continue
            if not isinstance(row, (list, tuple)) or len(row) == 0:
                continue
            _deserialize_io_row(field, ind, row)


def _io_global_index(field: str, ind: int) -> int:
    """
    k globale come in SCL:
      di -> k = ind
      ai -> k = (MAX_DI+1) + ind
      do -> k = (MAX_AI+1) + (MAX_DI+1) + ind
      ao -> k = (MAX_DO+1) + (MAX_AI+1) + (MAX_DI+1) + ind
      ri -> k = (MAX_AO+1) + (MAX_DO+1) + (MAX_AI+1) + (MAX_DI+1) + ind
    """
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
    k = _io_global_index(field, ind)
    if k > getattr(data_config, "MAX_IO", k):
        return

    # row: [Name, bool..., int..., dint..., real..., exprint..., exprreal...]
    name = str(row[0])
    data_config.IO_Name[k] = name
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
                    data_config.IO_Param[k].exprrealval[j] = _to_float(val, 0.0)
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


def _build_io_lists():
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


# ------------------ OBJ/AXIS ------------------
def _deserialize_obj_axis(data: Dict[str, Any]) -> None:
    """
    Deserializza i blocchi 'axis' dal YAML e popola correttamente
    tutti i campi di data_config.Axis_Param[i] (boolval, intval, realval, fcval, offsetval, typval)
    in base agli indici standard definiti in Type_AxisParam.
    """
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
        for j in range(min(len(bool_list), MAX_ASSEBOOL + 1)):
            data_config.Axis_Param[ind].boolval[j] = _bool_from_int(bool_list[j])
        # se meno valori → il resto default False
        for j in range(len(bool_list), MAX_ASSEBOOL + 1):
            data_config.Axis_Param[ind].boolval[j] = False

        # ======================
        # 📌 Intval[0..MAX_ASSEINT]
        # ======================
        int_list = _as_list(block.get("int"))
        for j in range(min(len(int_list), MAX_ASSEINT + 1)):
            data_config.Axis_Param[ind].intval[j] = _to_int(int_list[j], -1)
        for j in range(len(int_list), MAX_ASSEINT + 1):
            data_config.Axis_Param[ind].intval[j] = -1

        # ======================
        # 📌 Realvalcfg / Realval / Fcval / Offsetval / Typval
        # ======================
        real_list = _as_list(block.get("real"))
        for j in range(min(len(real_list), MAX_ASSEREAL + 1)):
            fv = _to_float(real_list[j], 0.0)
            data_config.Axis_Param[ind].realvalcfg[j] = fv
            data_config.Axis_Param[ind].realval[j] = fv

        type_list = _as_list(block.get("type"))
        for j in range(min(len(type_list), MAX_ASSEREAL + 1)):
            data_config.Axis_Param[ind].typval[j] = type_list[j]

        # TODO: controllare
        # # Se ci sono meno valori real → completa con 0.0
        # for j in range(len(real_list), MAX_ASSEREAL + 1):
        #     data_config.Axis_Param[ind].realvalcfg[j] = 0.0
        #     data_config.Axis_Param[ind].realval[j] = 0.0
        #     data_config.Axis_Param[ind].typval[j] = 0
        #     data_config.Axis_Param[ind].fcval[j] = 1.0
        #     data_config.Axis_Param[ind].offsetval[j] = 0.0


# ------------------ INPUT / OUTPUT / FB / PID / MOT / ALARM / MAINT / TOOLSET ------------------
def _deserialize_obj_input(data: Dict[str, Any]) -> None:
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


def _deserialize_obj_output(data: Dict[str, Any]) -> None:
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


def _deserialize_obj_fb(data: Dict[str, Any]) -> None:
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


def _deserialize_obj_pid(data: Dict[str, Any]) -> None:
    rows = _as_list(data.get("obj", {}).get("pid"))
    for ind, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            continue
        for j in range(MAX_PIDREAL + 1):
            val = row[j] if j < len(row) else 0.0
            data_config.PID_Param[ind].realval[j] = _to_float(val)


def _deserialize_obj_mot(data: Dict[str, Any]) -> None:
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


def _deserialize_obj_alarm(data: Dict[str, Any]) -> None:
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


def _deserialize_obj_maint(data: Dict[str, Any]) -> None:
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


def _deserialize_obj_toolset(data: Dict[str, Any]) -> None:
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

        # real (+ tipval,fc,offset tutti MISURA_LUNGH)
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
    is_system = decode_sys_addr(Ind)
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


def get_axis_name(Ind: int):
    return data_config.Axis_Name[Ind]


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
                if pid < len(IN_IND_MAP):
                    entry = IN_IND_MAP[pid]
                    label = entry.get("label")
                    display = entry.get("display", label)
                    origin = entry.get("origin", "??")
                    txt = f'{origin}\t→\t{display}'
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
                if pid < len(OUT_IND_MAP):
                    entry = OUT_IND_MAP[pid]
                    label = entry.get("label")
                    display = entry.get("display", label)
                    origin = entry.get("origin", "??")
                    txt = f'{origin}\t→\t{display}'
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
        elif iotype == IO_DO:
            OutputParamIntVals = data_config.Output_Param[outputInd].intval
            if OutputParamIntVals[OUTPUT_INT_TIPO] not in [OUTPUT_ADV, OUTPUT_PSLCAN]:
                for idx, val in enumerate(OutputParamIntVals):
                    idx_name = Type_OutputParam_Map["_intval"][idx]
                    output_Type = Type_OutputParam_Map["intval"][idx_name].get("type", [])
                    if iotype in output_Type:
                        if val == ind_target:
                            display = Type_OutputParam_Map["intval"][idx_name]["display"]
                            origin = Type_OutputParam_Map["intval"][idx_name]["origin"]
                            txt = f"{origin.format(idx)}\t→\t{display}"
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
                                logging.info(f"{origin.format(idx)}\t→\t{display}")
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
                                logging.info(f"{origin.format(idx)}\t→\t{display}")
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
            if FeedbackParamIntVals[FB_INT_TIPO] in [FB_AI, FB_AHSC, FB_AI2]:  # TODO: quello a ritenzione di analogico come si chiama?
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
                        if DEBUG_DEBUG_DEBUG:
                            logging.info('xERR_001')
                        continue
                    not_val, opnd_val, oper_val = data_config.IO_DI_List[Ind].exprintval[i:i + 3]
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
                        if DEBUG_DEBUG_DEBUG:
                            logging.info('xERR_001')
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
                        if DEBUG_DEBUG_DEBUG:
                            logging.info('xERR_001')
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
                        if DEBUG_DEBUG_DEBUG:
                            logging.info('xERR_001')
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
                        if DEBUG_DEBUG_DEBUG:
                            logging.info('xERR_001')
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
                txt = f"IO\t→\tDI\t→\t[{Ind}] {get_io_name(iotype=IO_DI, Ind=Ind)}\t→\tIn"
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
        run_io_expr_scan(iotype=IO_RI, ind_target=ind_target)
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


def decode_sys_addr(ind_target: int):
    """
    Decodifica un numero SYSTEM (>=2048) in (systyp, objind, elemind, sysname).
    Esempio:
        2113 → (1, 1, 1, "AXIS[1].UP")
    Ritorna None se il valore non è un indirizzo SYS valido.
    """
    if not isinstance(ind_target, int) or ind_target < BASE_AXIS:
        return None

    systyp = ind_target // BASE_AXIS
    objelemind = ind_target % BASE_AXIS

    if 1 <= systyp <= 7:  # TTTTT NNNNNN (Axis, Input, Output, ecc.)
        objind = objelemind % AXIS_GROUP_STEP
        elemind = objelemind // AXIS_GROUP_STEP
    elif 8 <= systyp <= 10:  # TTT NNNNNNNN (Alarm, Maint, BoolSystem)
        objind = objelemind % ALARM_GROUP_STEP
        elemind = objelemind // ALARM_GROUP_STEP
    else:
        return None

    # Nome descrittivo opzionale (solo se vuoi stamparlo)
    systype_names = {
        1: "AXIS",
        2: "FEEDBACK",
        3: "INPUT",
        4: "OUTPUT",
        5: "MOTOR",
        6: "PID",
        7: "TOOLSET",
        8: "ALARM",
        9: "MAINT",
        10: "BOOLSYSTEM",
    }

    sysaxis_names = {
        0: "MOVING", 1: "UP", 2: "DOWN", 3: "MAX", 4: "MIN", 5: "SUPLS", 6: "INFLS",
        7: "HH", 8: "H", 9: "L", 10: "LL", 11: "H0", 12: "L0", 13: "SAF", 14: "ALTFB",
        15: "BAD", 16: "TILT", 17: "P1UP", 18: "P1DOWN", 19: "P2UP", 20: "P2DOWN",
        21: "SLOW", 22: "FAST"
    }

    systyp_name = systype_names.get(systyp, f"TYPE{str(systyp)}")

    if systyp == 1:
        elem_name = sysaxis_names.get(elemind, f"ELEM{elemind}")
    else:
        elem_name = f"ELEM{elemind}"

    sysname = f"{systyp_name}[{get_axis_name(objind)}].{elem_name}"

    # return systyp, objind, elemind, sysname
    return sysname


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
    if iotype == IO_DI:
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
    logger.info("IN: custom_function")

    def check_axis_flag() -> list[str]:
        logging.info('Controllo flag')
        """
        Controlla limiti e flag per ogni asse.
        Stampa warning prima del gruppo di riferimenti.
        """
        logging.debug("IN: check_axis_flag")

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
            (ASSE_INT_INDSHH, ASSE_BOOL_ENABSHH),
            (ASSE_INT_INDSH, ASSE_BOOL_ENABSH),
            (ASSE_INT_INDSL, ASSE_BOOL_ENABSL),
            (ASSE_INT_INDSLL, ASSE_BOOL_ENABSLL),
            (ASSE_INT_INDSH0, ASSE_BOOL_ENABSH0),
            (ASSE_INT_INDSL0, ASSE_BOOL_ENABSL0),
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
            except Exception:
                continue

            axis_name = get_axis_name(Ind=axisInd)
            local_buf: list[str] = []

            for int_idx, bool_idx in axis_pairs:
                if int_idx >= len(AxisParamIntVals) or bool_idx >= len(AxisParamBoolVals):
                    continue

                di_val = AxisParamIntVals[int_idx]
                flag = AxisParamBoolVals[bool_idx]
                label = _axis_label_from_int_idx(int_idx)
                sys_idx = _sys_index_for(axisInd, label)

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

                if refs or di_val > 0:
                    # ⚠️ warning PRIMA
                    if not flag and (di_val > 0 or refs):
                        local_buf.append(
                            f"  ⚠️  Flag {label} disattivo ma {label}={di_val if di_val > 0 else 'SYS'} è impostato/usato")

                    # header label
                    local_buf.append(f"    ↳ Axes\t→\t[{axisInd}]{axis_name}\t→\t{label}")
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
                logging.info(f"\n[ASSE {axisInd:02d}] {axis_name}")
                logging.info("\n".join(local_buf))
                out_lines.append(f"[ASSE {axisInd:02d}] {axis_name}")
                out_lines.extend(local_buf)

        logging.debug("OUT: check_axis_flag")
        return out_lines

    def check_duplicate_do_ao_usage():
        """
        Controlla se una DO/AO è referenziata in più punti nel progetto.
        Usa run_io_scan per verificare dove viene utilizzata ogni uscita.
        """
        logging.info('-' * 60)
        logging.info('Controllo duplicati output')
        duplicates = {}

        for iotype, label in [(IO_DO, "DO"), (IO_AO, "AO")]:
            io_list = data_config.IO_DO_List if iotype == IO_DO else data_config.IO_AO_List

            for idx in range(len(io_list)):
                used_in = run_io_search(iotype=iotype, Ind=idx, verbose=False)
                if len(used_in) > 1:
                    io_name = get_io_name(iotype=iotype, Ind=idx)
                    duplicates[io_name or f"{label}[{idx}]"] = used_in
                    logging.info(f"⚠️ {label}[{idx}] {io_name or ''} usato in più punti:")
                    for u in used_in:
                        logging.info(f"   ↳ {u}")
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
                logging.info("⚠️ Duplicazioni trovate:")
                for cat, items in duplicates.items():
                    for ind, axes in items.items():
                        logging.info(f" - {cat.upper()}[{ind}] usato in: {', '.join(axes)}")
        logging.info('🔍 Fine controllo duplicati Input/Output/Feedback.')
        return duplicates

    def clean_di_axis_check() -> None:
        logging.info("🔍 Avvio controllo axis_flag_checks...")
        for axisInd in range(0, MAX_ASSE):
            AxisParamIntVals = data_config.Axis_Param[axisInd].intval
            to_check = [ASSE_INT_INDSHH, ASSE_INT_INDSH, ASSE_INT_INDSL, ASSE_INT_INDSLL, ASSE_INT_INDSH0, ASSE_INT_INDSL0]
            to_check.extend([ASSE_INT_FREE_71, ASSE_INT_FREE_72, ASSE_INT_OPTPARAM1IND, ASSE_INT_OPTPARAM2IND, ASSE_INT_OPTPARAM3IND])
            for idx in to_check:
                idx_name = Type_AxisParam_Map["_intval"][idx]
                if AxisParamIntVals[idx] != -1:
                    display = Type_AxisParam_Map["intval"][idx_name]["display"]
                    origin = Type_AxisParam_Map["intval"][idx_name]["origin"]
                    axis_name = get_axis_name(Ind=axisInd)
                    logging.info(f"⚠️ {origin.format(axisInd, axis_name)}\t→\t{display}\t[{AxisParamIntVals[idx]}] {get_io_name(iotype=IO_DI, Ind=AxisParamIntVals[idx])}")
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
                    logging.info(f"\n⚠️  Duplicati trovati in {label}:")
                    # ordina per tipo per renderlo più leggibile
                    for (tp, a1, a2), entries in sorted(dup_group.items(), key=lambda x: x[0]):
                        joined = ", ".join([f"[{idx}] {nm}" for idx, nm in entries])
                        logging.info(f"   → {'PNET' if tp == IO_TYPE_PNET else 'CAN' if tp == IO_TYPE_CAN else 'SW'} {a1}.{a2:<3} → {joined}")
            if not duplicates and verbose:
                logging.info("✅ Nessun duplicato di indirizzo trovato negli IO.")

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
                addr_str = f"{addr1}" # {addr2}"
                if addr_str in fAddresses:
                    io_name = get_io_name(iotype=IO_DI, Ind=Ind)
                    logging.info(f"⚠️ Safety non permesso in DI [{Ind}] {io_name} at address {addr_str}")
        for Ind in range(0, len(data_config.IO_AI_List)):
            if data_config.IO_AI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_PNET:
                addr1 = data_config.IO_AI_List[Ind].intval[IO_INT_ADDR1]
                # addr2 = data_config.IO_AI_List[Ind].intval[IO_INT_ADDR2]
                addr_str = f"{addr1}" # {addr2}"
                if addr_str in fAddresses:
                    io_name = get_io_name(iotype=IO_AI, Ind=Ind)
                    logging.info(f"⚠️  Safety non permesso in AI [{Ind}] {io_name} at address {addr_str}")
        for Ind in range(0, len(data_config.IO_DO_List)):
            if data_config.IO_DO_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_PNET:
                addr1 = data_config.IO_DO_List[Ind].intval[IO_INT_ADDR1]
                # addr2 = data_config.IO_DO_List[Ind].intval[IO_INT_ADDR2]
                addr_str = f"{addr1}" # {addr2}"
                if addr_str in fAddresses:
                    io_name = get_io_name(iotype=IO_DO, Ind=Ind)
                    logging.info(f"⚠️ Safety non permesso in DO [{Ind}] {io_name} at address {addr_str}")
        for Ind in range(0, len(data_config.IO_AO_List)):
            if data_config.IO_AO_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_PNET:
                addr1 = data_config.IO_AO_List[Ind].intval[IO_INT_ADDR1]
                # addr2 = data_config.IO_AO_List[Ind].intval[IO_INT_ADDR2]
                addr_str = f"{addr1}" # {addr2}"
                if addr_str in fAddresses:
                    io_name = get_io_name(iotype=IO_AO, Ind=Ind)
                    logging.info(f"⚠️ Safety non permesso in AO [{Ind}] {io_name} at address {addr_str}")
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
                    mismatches.append((axisInd, axis_name, tipo_asse, tipo_fb_alt, fb_ind))

        if mismatches:
            logging.info(f"\n⚠️  Assi con tipo misura diverso (ASSE_INT_TIPOMISURA ≠ FB_INT_TIPOMISURA):")
            for idx, axis_name, t_ass, t_fb, fb_name in mismatches:
                logging.info(f"   → [{idx:02d}] {axis_name:<20} ASSE={t_ass:<3}  FB={t_fb:<3}  ({fb_name})")
        else:
            logging.info("✅ Tutti gli assi hanno lo stesso tipo di misura tra ASSE e FB.")

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
            logging.info("\n⚠️  Duplicati trovati in AxisFunInd:")
            for axisInd, fun_list in duplicates.items():
                axis_name = getattr(data_config.Axis_Param[axisInd], "name", f"AXIS[{axisInd}]")
                fun_str = ", ".join([f"{Type_AxisFunInd[fi]}" for fi in fun_list])
                logging.info(f"   → {axis_name:<20} (axisOil {axisInd}) usato in FunInd: {fun_str}")

        logging.info("🔍 Fine controllo duplicati AxisFunInd.")
        return duplicates

    def check_lat_sup() -> None:
        logging.info("🔍 Avvio controllo supporti laterali")
        foo = [FUN_AXIS_PRESIDESUPP, FUN_AXIS_BENDSIDESUPP]
        for i in foo:
            if data_config.AxisFunInd[i] == -1:
                logging.info("Indice non configurato in Params > Functions")
            else:
                axis = data_config.Axis_Param[data_config.AxisFunInd[i]]
                axis_name = data_config.Axis_Name[data_config.AxisFunInd[i]] or f"AXIS_{data_config.AxisFunInd[i]}"
                tipo_asse = axis.intval[ASSE_INT_TIPOMISURA]
                if tipo_asse != MISURA_GRAD:
                    logging.info(f"⚠️ [{data_config.AxisFunInd[i]}]{axis_name} non ha il tipo di misura GRAD")
                if data_config.Axis_Param[i].intval[ASSE_INT_FEEDBACK] != -1:
                    axis_feedback = data_config.Feedback_Param[data_config.Axis_Param[i].intval[ASSE_INT_FEEDBACK]]
                    tipo_feedback = axis_feedback.intval[FB_INT_TIPOMISURA]
                    if tipo_feedback != MISURA_GRAD:
                        logging.info(f"⚠️ [{data_config.AxisFunInd[i]}]{axis_name} il feedback non ha il tipo di misura GRAD")
                if axis.boolval[ASSE_BOOL_MANSPDOWN]:
                    logging.info(f"⚠️ [{data_config.AxisFunInd[i]}]{axis_name} ha il flag MANSPDOWN attivo!")
        foo = {
            "REAL_LATSUPQ0": REAL_LATSUPQ0,
            "REAL_LATSUPQ1": REAL_LATSUPQ1,
            "REAL_LATSUPQ2": REAL_LATSUPQ2,
            "REAL_LATSUPQ3": REAL_LATSUPQ3,
            "REAL_LATSUPQ4": REAL_LATSUPQ4,
        }
        for label, idx in foo.items():
            if data_config.ParamRealType[idx] != -1:
                logging.info(f"⚠️ Config\t→\tLat\t→\t{label.replace('REAL_', '')} deve essere impostato -")
        logging.info("🔍 Fine controllo supporti laterali...")

    def check_oil_temp() -> None:
        logging.info("🔍 Inizio controllo olio...")
        # il numero rappresenta il tipo di dato MISURA_*
        _ = {
            ASSE_REAL_SRTUP: -1,
            ASSE_REAL_SRTDOWN: -1,
            ASSE_REAL_COEFFUP: -1,
            ASSE_REAL_COEFFDOWN: -1,
            ASSE_REAL_P1UP: 1,
            ASSE_REAL_P1DOWN: 1,
            ASSE_REAL_P2UP: 1,
            ASSE_REAL_P2DOWN: 1,
            ASSE_REAL_SYSPRESSUP1: 1,
            ASSE_REAL_SYSPRESSDOWN1: 1,
            ASSE_REAL_SYSPRESSUP2: 1,
            ASSE_REAL_SYSPRESSDOWN2: 1,
            ASSE_REAL_SYSPRESSUP3: 1,
            ASSE_REAL_SYSPRESSDOWN3: 1,
            ASSE_REAL_BWVMAX: 10,
            ASSE_REAL_DSMAXDOWN: -1,
            ASSE_REAL_DSMAXUP: -1,
            ASSE_REAL_FWVMAX: 10,
            ASSE_REAL_SMAX: 2,
            ASSE_REAL_SMIN: 2,
            ASSE_REAL_SSUP: 2,
            ASSE_REAL_SINF: 2,
            ASSE_REAL_VMINSTARTED: 10,
            ASSE_REAL_SHH: 2,
            ASSE_REAL_SH: 2,
            ASSE_REAL_SL: 2,
            ASSE_REAL_SLL: 2,
            ASSE_REAL_TILTMAX: -1,
        }
        diff = False
        if data_config.AxisFunInd[FUN_AXIS_OILTEMP] != -1:
            axisOil = data_config.Axis_Param[data_config.AxisFunInd[FUN_AXIS_OILTEMP]]
            for i, value in _.items():
                if axisOil.typval[i] != value:
                    logging.info(f'now:{axisOil.typval[i]} shoudbe:{_[i]} id: {i}')
                    diff = True
            if diff:
                logging.info("  type: [-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,10,-1,-1,10,2,2,2,2,10,2,2,2,2,-1,-1,-1,-1,-1,-1,-1,-1,-1,2,2,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]")
        logging.info("🔍 Fine controllo olio...")

    def check_release() -> None:
        logging.info("🔍 Inizio controllo sgancio...")
        if data_config.AxisFunInd[FUN_AXIS_DE] == -1:
            logging.info("Indice DE non configurato in Params > Functions")
            return
        if data_config.AxisFunInd[FUN_AXIS_PINCH] == -1:
            logging.info("Indice B non configurato in Params > Functions")
            return
        pinchName = f"[{data_config.AxisFunInd[FUN_AXIS_PINCH]}]{data_config.Axis_Name[data_config.AxisFunInd[FUN_AXIS_PINCH]] or f'AXIS_{data_config.AxisFunInd[FUN_AXIS_DE]}'}"
        safetyDown = [
            ASSE_INT_SAFETYDOWNIND1, ASSE_INT_SAFETYDOWNIND2, ASSE_INT_SAFETYDOWNIND3,
            ASSE_INT_SAFETYDOWNIND4, ASSE_INT_SAFETYDOWNIND5, ASSE_INT_SAFETYDOWNIND6
        ]
        if not any(make_axis_sys_addr(AXIS_GROUPS_ORDER[IO_SYSAXIS_L], data_config.AxisFunInd[FUN_AXIS_PINCH]) == data_config.Axis_Param[FUN_AXIS_DE].intval[x] for x in safetyDown):
            logging.info(f"⚠️ {pinchName}.L non è presente negli interlock down direttamente va aggiunto!")
        safetyUp = [
            ASSE_INT_SAFETYUPIND1, ASSE_INT_SAFETYUPIND1, ASSE_INT_SAFETYUPIND1,
            ASSE_INT_SAFETYUPIND1, ASSE_INT_SAFETYUPIND1, ASSE_INT_SAFETYUPIND1
        ]
        if any(make_axis_sys_addr(AXIS_GROUPS_ORDER[IO_SYSAXIS_L], data_config.AxisFunInd[FUN_AXIS_PINCH]) == data_config.Axis_Param[FUN_AXIS_DE].intval[x] for x in safetyUp):
            logging.info(f"⚠️ {pinchName}.L è presente negli interlock up va rimosso!")
        # conrtollo flag

        # controllo quota apertura sgancio
        if data_config.Axis_Param[data_config.AxisFunInd[FUN_AXIS_PINCH]].realval[ASSE_REAL_SHH] <= data_config.Axis_Param[data_config.AxisFunInd[FUN_AXIS_PINCH]].realval[ASSE_REAL_SL]:
            logging.info(f"⚠️ {pinchName}.HH è minore o uguale a {pinchName}.L quota reset automatico")
        logging.info("🔍 Fine controllo sgancio...")

    def check_safety() -> None:
        if data_config.ParamInt[INT_HOLDTORUNTYPE] != SAFETY_INT:
            logging.info("⚠️ Hold to run non impostato su INT")
    
    def check_rotation() -> None:
        logging.info("🔍 Inizio controllo rotazione...")
        axisInd = data_config.AxisFunInd[FUN_AXIS_ROT]
        if axisInd != -1:
            axis = data_config.Axis_Param[axisInd]
            axis_name = data_config.Axis_Name[axisInd] or f"AXIS_{axisInd}"
            for i in [ASSE_REAL_SMAX, ASSE_REAL_SHH]:
                if axis.realval[i] != 999999:
                    logging.info(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][i]]['display']} non impostato a +999999.0 ma a {axis.realval[i]}")
            for i in [ASSE_REAL_SMIN, ASSE_REAL_SLL]:
                if axis.realval[i] != -999999:
                    logging.info(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][i]]['display']} non impostato a -999999.0 ma a {axis.realval[i]}")
            if axis.realval[ASSE_REAL_SH] != 500:
                logging.info(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SH]]['display']} non impostato a 500.0 ma a {axis.realval[ASSE_REAL_SH]}")
            if axis.realval[ASSE_REAL_SL] != -500:
                logging.info(f"⚠️ [{axisInd}]{axis_name} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][ASSE_REAL_SL]]['display']} non impostato a -500.0 ma a {axis.realval[ASSE_REAL_SL]}")
        logging.info("🔍 Fine controllo rotazione...")

    def geometry_check() -> None:
        logging.info("🔍 Inizio controllo geometria...")
        model = data_config.ParamString[0][-4:]
        model_width = model[:2] + '00'
        top_roll_diameter = model[2:] + '0'
        try:
            model_width = int(model_width)
        except ValueError:
            logging.info("Modello non rilevato")
            return

        if model_width > data_config.ParamReal[REAL_WIDTH]:
            logging.info(f"⚠️ Modello macchina {model}, lunghezza tavola in geometria più piccolo: {data_config.ParamReal[REAL_WIDTH]}")

        try:
            top_roll_diameter = int(top_roll_diameter)
        except ValueError:
            logging.info("Diametro rullo non rilevato")
            return

        if top_roll_diameter > data_config.ParamReal[REAL_TROUTERDIAM]:
            logging.info(f"⚠️ Modello macchina {model}, diametro rullo superiore maggiore di quello in geo: {data_config.ParamReal[REAL_TROUTERDIAM]}")
        elif top_roll_diameter < data_config.ParamReal[REAL_TROUTERDIAM]:
            logging.info(f"⚠️ Modello macchina {model}, diametro rullo superiore minore di quello in geo: {data_config.ParamReal[REAL_TROUTERDIAM]}")
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
                            logging.info(f"⚠️ [{i}]{slaveAxisName} ha il parametro {Type_AxisParam_Map['realval'][Type_AxisParam_Map['_realval'][x]]['display']} diverso da [{masterAxisInd}]{masterAxisName}")
        logging.info("🔍 Fine controllo velocità master/slave...")

    foo = [check_axis_flag, check_duplicate_do_ao_usage, check_duplicate_obj_usage, clean_di_axis_check, duplicate_io_address,
           check_axis_um, check_duplicate_funaxis, check_lat_sup, check_oil_temp, check_release, check_safety, check_rotation,
           geometry_check, check_axis_speed_master_slave, check_forbidden_ao_do_usage]
    for func in foo:
        logging.info('-' * 60)
        func()
    logger.info("OUT: custom_function")


if __name__ == "__main__":
    populate_from_yaml_file("../../config.yaml")
    custom_function()
    run_io_search(IO_DI, 2506, verbose=True)
    while True:
        logging.info(", ".join([f"{name.replace('IO_', '')}={globals()[name]}" for name in ["IO_DI", "IO_AI", "IO_DO", "IO_AO", "IO_RI"]]))
        _type = input()
        _target = input('Target:')

        try:
            _type = int(_type)
            _target = int(_target)
        except:
            continue

        run_io_search(_type, _target, verbose=True)
