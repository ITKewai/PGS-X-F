#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/db/data_config.py
---------------------------------
Replica in Python la deserializzazione del config YAML (ristrutturato da load_yaml)
verso l'istanza DATA_CONFIG, seguendo la logica SCL.
"""
from __future__ import annotations
import logging

from pathlib import Path
from typing import Any, List, Dict, Sequence, Optional

from utils.exports.tia_constants_map import *
from utils.yaml.load import load_yaml
from utils.exports.tia_constants import *  # noqa: F401,F403  (porta DATA_CONFIG, MAX_*, costanti simboliche, UDT, ecc.)

logging.basicConfig(
        level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"  # <-- formato orario (solo ore:minuti:secondi)
)

logger = logging.getLogger(__name__)  # crea un logger con il nome del file

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
    _deserialize_card_exc(data)            # card / exc
    _deserialize_axind_in_out(data)        # axind / in / out (indici mapping rapidi)
    _deserialize_io(data)                  # di / ai / do / ao / ri   (da data['io'])
    _deserialize_obj_axis(data)            # axis/bool/int/real/type  (da data['obj']['axis'])
    _deserialize_obj_input(data)           # input                    (da data['obj']['input'])
    _deserialize_obj_output(data)          # output                   (da data['obj']['output'])
    _deserialize_obj_fb(data)              # fb                       (da data['obj']['fb'])
    _deserialize_obj_pid(data)             # pid                      (da data['obj']['pid'] se presente)
    _deserialize_obj_mot(data)             # mot                      (da data['obj']['mot'])
    _deserialize_obj_alarm(data)           # alarm                    (da data['obj']['alarm'])
    _deserialize_obj_maint(data)           # maint                    (da data['obj']['maint'])
    _deserialize_obj_toolset(data)         # toolset                  (da data['obj']['toolset'])
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
    pbool   = _as_list(param.get("pbool"))
    pint    = _as_list(param.get("pint"))
    preal   = _as_list(param.get("preal"))
    ptype   = _as_list(param.get("ptype"))

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

            # Tipologia, FC e offset: prendiamo da UM (unità di misura) se disponibile
            try:
                MISURA_LUNGH = getattr(data_config, "MISURA_LUNGH")
                data_config.Axis_Param[ind].typval[j] = MISURA_LUNGH
                data_config.Axis_Param[ind].fcval[j] = data_config.UM_FC[MISURA_LUNGH]
                data_config.Axis_Param[ind].offsetval[j] = data_config.UM_Offset[MISURA_LUNGH]
            except Exception:
                data_config.Axis_Param[ind].typval[j] = 0
                data_config.Axis_Param[ind].fcval[j] = 1.0
                data_config.Axis_Param[ind].offsetval[j] = 0.0

        # Se ci sono meno valori real → completa con 0.0
        for j in range(len(real_list), MAX_ASSEREAL + 1):
            data_config.Axis_Param[ind].realvalcfg[j] = 0.0
            data_config.Axis_Param[ind].realval[j] = 0.0
            data_config.Axis_Param[ind].typval[j] = 0
            data_config.Axis_Param[ind].fcval[j] = 1.0
            data_config.Axis_Param[ind].offsetval[j] = 0.0


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
def _finalize_config(data: Dict[str, Any]) -> None:
    """ Allineamenti finali a EOF """
    try:
        HEADER_SN = getattr(data_config, "HEADER_SN")
        INT_SN = getattr(data_config, "INT_SN")
        data_config.Config_Header[HEADER_SN] = data_config.ParamInt[INT_SN]
    except Exception:
        pass

    try:
        HEADER_TYPEVERSION = getattr(data_config, "HEADER_TYPEVERSION")
        HEADER_FILEVERSION = getattr(data_config, "HEADER_FILEVERSION")
        if data_config.Config_Header[HEADER_TYPEVERSION] != data_config.CFGVersion:
            data_config.Config_Header[HEADER_TYPEVERSION] = data_config.CFGVersion
            data_config.Config_Header[HEADER_FILEVERSION] = 0
    except Exception:
        pass


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
        if name == 'None':
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
        print(f'{idx}\t{display}\t-\tx{val}\t-\t{origin}')


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
        print(f'{idx}\t{display}\t-\tx{val}\t-\t{origin}')


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
        print(f'{idx}\t{display}\t-\tx{val}\t-\t{origin}')


def _debug_ioparam(iotype: int, Ind: int = 0):
    if iotype == IO_DI:
        print(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_DI_List[Ind]}')
    elif iotype == IO_DO:
        print(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_DO_List[Ind]}')
    elif iotype == IO_AI:
        print(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_AI_List[Ind]}')
    elif iotype == IO_AO:
        print(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_AO_List[Ind]}')
    elif iotype == IO_RI:
        print(f'[{Ind}] - "{get_io_name(iotype=iotype, Ind=Ind)}"\t{data_config.IO_RI_List[Ind]}')


def run_params_scan(iotype: int, ind_target: int):
    logger.debug('IN: run_params_scan')
    if iotype == IO_DI:
        for pid, val in enumerate(data_config.InInd):
            if val == ind_target:
                if pid < len(IN_IND_MAP):
                    entry = IN_IND_MAP[pid]
                    label = entry.get("label")
                    display = entry.get("display", label)
                    origin = entry.get("origin", "??")
                    print(f'{origin}\t→\t{display}')

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
                    print(f"{origin}\t→\t{display}")
    elif iotype == IO_DO:
        for pid, val in enumerate(data_config.OutInd):
            if val == ind_target:
                if pid < len(OUT_IND_MAP):
                    entry = OUT_IND_MAP[pid]
                    label = entry.get("label")
                    display = entry.get("display", label)
                    origin = entry.get("origin", "??")
                    print(f'{origin}\t→\t{display}')

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
                    print(f"{origin}\t→\t{display}")


def run_axis_scan(iotype: int, ind_target: int = None, axisInd: int = None):
    if axisInd is None:
        logging.debug('IN: run_axis_scan')
    """
    iotype: tipo di io
    Ind: indice da cercare
    axisInd: asse dove cercarlo
    """
    if axisInd is not None:
        if iotype == IO_DI:
            AxisParamIntVals = data_config.Axis_Param[axisInd].intval
            for idx,val in enumerate(AxisParamIntVals):
                idx_name = Type_AxisParam_Map["_intval"][idx]
                axis_Type = Type_AxisParam_Map["intval"][idx_name].get("type", [])
                if iotype in axis_Type:
                    if val == ind_target:
                        display = Type_AxisParam_Map["intval"][idx_name]["display"]
                        origin = Type_AxisParam_Map["intval"][idx_name]["origin"]
                        axis_name = get_axis_name(Ind=axisInd)
                        print(f"{origin.format(axisInd, axis_name)}\t→\t{display}")
    else:
        for i in range(0, MAX_ASSE):
            run_axis_scan(iotype=iotype, ind_target=ind_target, axisInd=i)
    if axisInd is None:
        logging.debug('OUT: run_axis_scan')


def run_input_scan(iotype: int, ind_target: int = None, inputInd: int = None):
    if inputInd is None:
        logging.debug('IN: run_input_scan')
    """
    iotype: tipo di io
    Ind: indice da cercare
    InputInd: input dove cercarlo
    """
    if iotype == IO_DI:
        if inputInd is not None:
            InputParamIntVals = data_config.Input_Param[inputInd].intval
            for idx,val in enumerate(InputParamIntVals):
                idx_name = Type_InputParam_Map["_intval"][idx]
                input_Type = Type_InputParam_Map["intval"][idx_name].get("type", [])
                if iotype in input_Type:
                    if val == ind_target:
                        display = Type_InputParam_Map["intval"][idx_name]["display"]
                        origin = Type_InputParam_Map["intval"][idx_name]["origin"]
                        print(f"{origin.format(inputInd)}\t→\t{display}")
        else:
            for i in range(0, MAX_INPUT):
                run_input_scan(iotype=iotype, ind_target=ind_target, inputInd=i)
    if inputInd is None:
        logging.debug('OUT: run_input_scan')


def run_output_scan(iotype: int, ind_target: int = None, outputInd: int = None):
    if outputInd is None:
        logging.debug('IN: run_output_scan')
    """
    iotype: tipo di io
    Ind: indice da cercare
    outputInd: output dove cercarlo
    """
    if outputInd is not None:
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
                        print(f"{origin.format(outputInd)}\t→\t{display}")
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
                            print(f"{origin.format(idx)}\t→\t{display}")
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
                            print(f"{origin.format(outputInd)}\t→\t{display}")
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
                            print(f"{origin.format(outputInd)}\t→\t{display}")
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
                            print(f"{origin.format(outputInd)}\t→\t{display}")
                    else:
                        logging.warning(f'{idx_name} non definito')

    else:
        for i in range(0, MAX_OUTPUT):
            run_output_scan(iotype=iotype, ind_target=ind_target, outputInd=i)
    if outputInd is None:
        logging.debug('OUT: run_output_scan')


def run_feedback_scan(iotype: int, ind_target: int = None, feedbackInd: int = None):
    if feedbackInd is None:
        logging.debug('IN: run_feedback_scan')
    """
    iotype: tipo di io
    Ind: indice da cercare
    feedbackInd: output dove cercarlo
    """
    if iotype == IO_DI:
        if feedbackInd is not None:
            FeedbackParamIntVals = data_config.Feedback_Param[feedbackInd].intval
            if FeedbackParamIntVals[FB_INT_RESETIND] == ind_target:
                origin = Type_FeedbackParam_Map["intval"]["FB_INT_RESETIND"]["origin"]
                display = Type_FeedbackParam_Map["intval"]["FB_INT_RESETIND"]["display"]
                print(f"{origin.format(feedbackInd)}\t→\t{display}")
            if FeedbackParamIntVals[FB_INT_TIPO] == FB_DI:
                if FeedbackParamIntVals[FB_INT_ININD] == ind_target:
                    origin = Type_FeedbackParam_Map["intval"]["FB_INT_ININD"]["origin"]
                    display = Type_FeedbackParam_Map["intval"]["FB_INT_ININD"]["display"]
                    print(f"{origin.format(feedbackInd)}\t→\t{display}")
        else:
            for i in range(0, MAX_FEEDBACK):
                run_feedback_scan(iotype=iotype, ind_target=ind_target, feedbackInd=i)
    if feedbackInd is None:
        logging.debug('OUT: run_feedback_scan')


def run_io_expr_scan(iotype: int, ind_target: int = None):
    logger.debug('IN: run_io_expr_scan')
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
                            print('xERR_001')
                        continue
                    not_val, opnd_val, oper_val = data_config.IO_DI_List[Ind].exprintval[i:i + 3]
                    if not_val in [IO_EXPR_NONE, IO_EXPR_VAL, IO_EXPR_NOTVAL]:
                        group_num = ((i - 1) // 3) + 1
                        if opnd_val == ind_target:
                            print(f"IO\t→\tDI\t→\t[{Ind}] {get_io_name(iotype=IO_DI, Ind=Ind)}\t→\tExpr\t→\tN{group_num}")
    elif iotype == IO_AI:
        for Ind in range(0, len(data_config.IO_DI_List)):
            if data_config.IO_DI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
                if len(data_config.IO_DI_List[Ind].exprintval) <= 1:
                    continue
                expr_type = data_config.IO_DI_List[Ind].exprintval[0]
                # 🔁 Ciclo sui gruppi (partendo da index 1, passo di 3)
                for i in range(1, len(data_config.IO_DI_List[Ind].exprintval), 3):
                    if i + 2 >= len(data_config.IO_DI_List[Ind].exprintval):
                        if DEBUG_DEBUG_DEBUG:
                            print('xERR_001')
                        continue
                    not_val, opnd_val, oper_val = data_config.IO_DI_List[Ind].exprintval[i:i + 3]
                    if not_val in [IO_EXPR_AIEQ0, IO_EXPR_AINE0, IO_EXPR_AIGT0,
                                   IO_EXPR_AIGE0, IO_EXPR_AILT0, IO_EXPR_AILE0]:
                        group_num = ((i - 1) // 3) + 1
                        if opnd_val == ind_target:
                            print(f"IO\t→\tDI\t→\t[{Ind}] {get_io_name(iotype=IO_DI, Ind=Ind)}\t→\tExpr\t→\tN{group_num}")

    logger.debug('OUT: run_io_expr_scan')


def run_io_scan(iotype: int, ind_target: int = None):
    logging.debug('IN: run_io_scan')
    if iotype == IO_DI:
        for Ind in range(0, len(data_config.IO_DI_List)):
            if data_config.IO_DI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
                if data_config.IO_DI_List[Ind].intval[IO_INT_TIMEOUT] == -1:
                    continue
                delay_di = data_config.IO_DI_List[Ind].intval[IO_INT_ININD]
                if delay_di and delay_di == ind_target:
                    print(f"IO\t→\tDI\t→\t[{Ind}] {get_io_name(iotype=IO_DI, Ind=Ind)}\t→\tIn")
                    # TODO: DI possono essere totman ecc ? se si fare ricerca

        run_io_expr_scan(iotype=IO_DI, ind_target=ind_target)

        for Ind in range(0, len(data_config.IO_DO_List)):
            if data_config.IO_DO_List[Ind].intval[IO_INT_ININD] == ind_target:
                print(f"IO\t→\tDO\t→\t[{Ind}] {get_io_name(iotype=IO_DO, Ind=Ind)}\t→\tIn")
        for Ind in range(0, len(data_config.IO_RI_List)):
            if data_config.IO_RI_List[Ind].intval[IO_INT_ADDRTYPE] in [IO_TYPE_FUNC_TOT, IO_TYPE_FUNC_TOTAUTO,
                                                                       IO_TYPE_FUNC_TOTMAN, IO_TYPE_FUNC_DTOT,
                                                                       IO_TYPE_FUNC_DTOTAUTO, IO_TYPE_FUNC_DTOTMAN,
                                                                       IO_TYPE_FUNC_TIME, IO_TYPE_FUNC_TIMEAUTO,
                                                                       IO_TYPE_FUNC_TIMEMAN, IO_TYPE_FUNC_DTIME,
                                                                       IO_TYPE_FUNC_DTIMEAUTO, IO_TYPE_FUNC_DTIMEMAN]:
                if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR1] == IO_DI:
                    if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR2] == ind_target:
                        print(f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tAddress")
            if data_config.IO_RI_List[Ind].intval[IO_INT_NBYTES] == ind_target:
                print(f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tEnabled")
            if data_config.IO_RI_List[Ind].intval[IO_INT_TIMEOUT] == ind_target:
                print(f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tReset")
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
                        print(f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tAddress")
    if iotype == IO_AI:
        # for Ind in range(0, len(data_config.IO_DI_List)):
        #     if data_config.IO_DI_List[Ind].intval[IO_INT_ADDRTYPE] == IO_TYPE_CALC:
        #         if data_config.IO_DI_List[Ind].intval[IO_INT_TIMEOUT] == -1:
        #             continue
        #         delay_di = data_config.IO_DI_List[Ind].intval[IO_INT_ININD]
        #         if delay_di and delay_di == ind_target:
        #             print(f"IO\t→\tDI\t→\t[{Ind}] {get_io_name(iotype=IO_AI, Ind=Ind)}\t→\tIn")
        #             TODO: DI possono essere totman ecc ? se si fare ricerca
        #
        run_io_expr_scan(iotype=IO_AI, ind_target=ind_target)

        # for Ind in range(0, len(data_config.IO_DO_List)):
        #     if data_config.IO_DO_List[Ind].intval[IO_INT_ININD] == ind_target:
        #         print(f"IO\t→\tDO\t→\t[{Ind}] {get_io_name(iotype=IO_DO, Ind=Ind)}\t→\tIn")
        # for Ind in range(0, len(data_config.IO_RI_List)):
        #     if data_config.IO_RI_List[Ind].intval[IO_INT_ADDRTYPE] in [IO_TYPE_FUNC_TOT, IO_TYPE_FUNC_TOTAUTO,
        #                                                                IO_TYPE_FUNC_TOTMAN, IO_TYPE_FUNC_DTOT,
        #                                                                IO_TYPE_FUNC_DTOTAUTO, IO_TYPE_FUNC_DTOTMAN,
        #                                                                IO_TYPE_FUNC_TIME, IO_TYPE_FUNC_TIMEAUTO,
        #                                                                IO_TYPE_FUNC_TIMEMAN, IO_TYPE_FUNC_DTIME,
        #                                                                IO_TYPE_FUNC_DTIMEAUTO, IO_TYPE_FUNC_DTIMEMAN]:
        #         if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR1] == IO_AI:
        #             if data_config.IO_RI_List[Ind].intval[IO_INT_ADDR2] == ind_target:
        #                 print(f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tAddress")
        #     if data_config.IO_RI_List[Ind].intval[IO_INT_NBYTES] == ind_target:
        #         print(f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tEnabled")
        #     if data_config.IO_RI_List[Ind].intval[IO_INT_TIMEOUT] == ind_target:
        #         print(f"IO\t→\tRI\t→\t[{Ind}] {get_io_name(iotype=IO_RI, Ind=Ind)}\t→\tReset")
    logging.debug('OUT: run_io_scan')


def run_alarm_scan(iotype: int, ind_target: int = None):
    logging.debug('IN: run_alarm_scan')
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
                        print(f"{origin.format(idx, alarm_name)}\t→\t{display}")
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
                        print(f"{origin.format(idx, alarm_name)}\t→\t{display}")
    logging.debug('OUT: run_alarm_scan')


def run_motor_scan(iotype: int, ind_target: int = None):
    logging.debug('IN: run_motor_scan')
    if iotype == IO_DI:
        for Ind in range(0, MAX_MOTORE):
            if data_config.Motor_LSInd[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tLS - STOP")
            if data_config.Motor_LS2Ind[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tLS2 - START")
            if data_config.Motor_TRInd[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tTR")
            if data_config.Motor_TR2Ind[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tTR2")
            if data_config.Motor_StatInd[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tSTAT")
            if data_config.Motor_StartingInd[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tSTARTING")
    elif iotype == IO_DO:
        for Ind in range(0, MAX_MOTORE):
            if data_config.Motor_CmdInd[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tCMD")
            if data_config.Motor_Cmd1Ind[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tCMD1")
            if data_config.Motor_Cmd2Ind[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tCMD2")
            if data_config.Motor_Cmd3Ind[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tCMD3")
    logging.debug('OUT: run_motor_scan')


def run_maintenance_scan(iotype: int, ind_target: int = None):
    logging.debug('IN: run_maintenance_scan')
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
                        print(f"{origin.format(idx, maint_name)}\t→\t{display}")
    elif iotype == IO_DO:
        for Ind in range(0, MAX_MAINT):
            if data_config.Motor_CmdInd[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tCMD")
            if data_config.Motor_Cmd1Ind[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tCMD1")
            if data_config.Motor_Cmd2Ind[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tCMD2")
            if data_config.Motor_Cmd3Ind[Ind] == ind_target:
                print(f"Motor\t→\t{Ind + 1}\t→\tCMD3")
    logging.debug('OUT: run_maintenance_scan')


def run_io_search(iotype: int, Ind: Optional[int] = None):
    logging.debug('IN: run_io_search')
    if iotype == IO_DI:
        run_io_scan(iotype=IO_DI, ind_target=Ind)
        run_params_scan(iotype=IO_DI, ind_target=Ind)
        run_motor_scan(iotype=IO_DI, ind_target=Ind)
        run_axis_scan(iotype=IO_DI, ind_target=Ind, axisInd=None)
        run_input_scan(iotype=IO_DI, ind_target=Ind, inputInd=None)
        run_output_scan(iotype=IO_DI, ind_target=Ind, outputInd=None)
        run_feedback_scan(iotype=IO_DI, ind_target=Ind, feedbackInd=None)
        run_alarm_scan(iotype=IO_DI, ind_target=Ind)
        run_maintenance_scan(iotype=IO_DI, ind_target=Ind)
    elif iotype == IO_DO:
        run_io_scan(iotype=IO_DO, ind_target=Ind)
        run_params_scan(iotype=IO_DO, ind_target=Ind)
        run_motor_scan(iotype=IO_DO, ind_target=Ind)
        # run_axis_scan(iotype=IO_DO, ind_target=Ind, axisInd=None) # TODO: Non ci sono?
        # run_input_scan(iotype=IO_DO, ind_target=Ind, inputInd=None) # TODO: Non ci sono?
        run_output_scan(iotype=IO_DO, ind_target=Ind, outputInd=None)
        # run_feedback_scan(iotype=IO_DO, ind_target=Ind, feedbackInd=None)
        run_alarm_scan(iotype=IO_DO, ind_target=Ind)
        # run_maintenance_scan(iotype=IO_DO, ind_target=Ind)
    elif iotype == IO_AI:
        run_io_scan(iotype=IO_AI, ind_target=Ind)
        # run_params_scan(iotype=IO_AI, ind_target=Ind)
        # run_motor_scan(iotype=IO_AI, ind_target=Ind)
        # run_axis_scan(iotype=IO_AI, ind_target=Ind, axisInd=None)
        # run_input_scan(iotype=IO_AI, ind_target=Ind, inputInd=None)
        # run_output_scan(iotype=IO_AI, ind_target=Ind, outputInd=None)
        # run_feedback_scan(iotype=IO_AI, ind_target=Ind, feedbackInd=None)
        # run_alarm_scan(iotype=IO_AI, ind_target=Ind)
        # run_maintenance_scan(iotype=IO_AI, ind_target=Ind)
    logging.debug('OUT: run_io_search')


if __name__ == "__main__":
    populate_from_yaml_file("../../config.yaml")
    while True:
        num = input('')
        try:
            num = int(num)
        except:
            continue
        run_io_search(IO_AI, num)
