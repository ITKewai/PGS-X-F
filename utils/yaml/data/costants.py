from typing import Dict
from utils.exports.tia_constants import *
# --- Mappe fornite ---
ADDRESS = {
    IO_TYPE_NONE: "",
    IO_TYPE_PNET: "PNET",
    IO_TYPE_CAN: "CAN",
    IO_TYPE_SW: "SW",
    IO_TYPE_CALC: "CALC",
    IO_TYPE_FUNC_TOT: "TOT",
    IO_TYPE_FUNC_TOTAUTO: "TOTAUTO",
    IO_TYPE_FUNC_TOTMAN: "TOTMAN",
    IO_TYPE_FUNC_DTOT: "DAILYTOT",
    IO_TYPE_FUNC_DTOTAUTO: "DAILYTOTAUTO",
    IO_TYPE_FUNC_DTOTMAN: "DAILYTOTMAN",
    IO_TYPE_FUNC_TIME: "TIME",
    IO_TYPE_FUNC_TIMEAUTO: "TIMEAUTO",
    IO_TYPE_FUNC_TIMEMAN: "TIMEMAN",
    IO_TYPE_FUNC_DTIME: "DAILYTIME",
    IO_TYPE_FUNC_DTIMEAUTO: "DAILYTIMEAUTO",
    IO_TYPE_FUNC_DTIMEMAN: "DAILYTIMEMAN",
}

UM = {
    -1: '',
    0: 'LUNG',
    1: 'PRESS',
    2: 'TEMP',
    3: 'VEL',
    4: 'YP',
    5: 'RAPP',
    6: 'VELASS',
    7: 'VELPRESS',
    8: 'AREA',
    9: 'ROT',
    10: 'E0',
    11: 'GRAD',
    12: 'NUM',
}

MEMTYPE = {
    -1: '',
    0: '',
    1: '',
    2: '',
    3: 'EVENTS',
    4: 'INT',
    5: 'REAL',
}

FB_TYPE = {
    -1: '',
    1: 'AI',
    2: 'DI',
    3: 'RHSC',
    4: 'AHSC',
    5: 'ATV340',
    6: 'INC',
    7: 'AI2',
}

FB_MESURETYPE = UM.copy()


IO_CAMPO_1 = {
    -1: '',
    IO_DI: 'DI',
    IO_AI: 'AI',
    IO_DO: 'DO',
    IO_AO: 'AO',
    IO_RI: 'RI',
}

EXPRTYPE = {
    -1: '',
    0: 'CYCLE',
    1: 'TRIGGER',
}

INPUT_MESURETYPE = UM.copy()

OUTPUT_TYPE = {
    -1: '',
    0: '',
    1: 'SEL',
    2: 'DIR',
    3: 'DIRINV',
    4: 'SELSLOW',
    5: 'ADV',
    6: 'PSLCAN',
    7: 'SELFL',
    8: 'SEL2PV',
    9: 'ATV340',
}

MOT_TYPE = {
    -1: '',
    0: 'M1',
    1: 'M2',
    2: 'M3',
    3: 'M4',
    4: 'M5',
    5: 'M6',
    6: 'M7',
    7: 'M8',
    8: 'Recycling',
    9: 'Cooling',
    10: 'Heating',
    11: 'RT',
    12: 'RT2',
    13: 'Flushing',
}
# SOLO SE ADDRESS == 4 SI ABILITANO I CAMPI TIMEOUT E IN
# EXPR_ADDRESS: intero "grezzo" (senza mappa)

EXPR_OPERAND = {
    -1: '-',
    0: '',
    1: 'NOT',
    2: 'AI == 0',
    3: 'AI != 0',
    4: 'AI > 0',
    5: 'AI >= 0',
    6: 'AI < 0',
    7: 'AI <= 0',
    8: 'RI == 0',
    9: 'RI != 0',
    10: 'RI > 0',
    11: 'RI >= 0',
    12: 'RI < 0',
    13: 'RI <= 0',
}

EXPR_OPERAND_DI = [-1, 0, 1]
EXPR_OPERAND_AI = [2, 3, 4, 5, 6, 7]
EXPR_OPERAND_RI = [8, 9, 10, 11, 12, 13]

EXPR_OPERATOR = {
    -1: '-',
    0: 'AND',
    1: 'OR',
}

AO_PRIORITY = {
    -1: 'FIRST',
    0: 'MIN'
}


# --- Indici attesi nella struttura obj>input ---
IDX_EXPRTYPE = 20
IDX_DI_IN = 13

IDX_AO_ADDRESS = 5
IDX_AO_IN = 12
IDX_AO_DUAL = 13

IDX_DO_IN = 13

IDX_FB_TYPE = 0
IDX_FB_RESETIND = 2
IDX_FB_ININD = 3
IDX_FB_ERR_DEPRECATED = 4

DI_NUM_EXPR_GROUPS = 8
DI_EXPR_GROUP_SIZE = 3  # (EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR)

IDX_INPUT_DIGUP1 = 5
IDX_INPUT_DIGDOWN1 = IDX_OUTPUT_RPM = IDX_OUTPUT_STATUS1PSLCAN = 6
IDX_OUTPUT_TIMEOUTBRKADV = IDX_INPUT_STATUS1PSLCAN = 7  # per PSLCAN → STATUS1PSLCAN
IDX_INPUT_DIGUP2 = IDX_OUTPUT_STATUS2PSLCAN = 8
IDX_INPUT_DIGDOWN2 = IDX_OUTPUT_FREE = IDX_INPUT_STATUS2PSLCAN = 9
IDX_INPUT_ACT = 11
IDX_INPUT_ENAB1 = 12
IDX_INPUT_ENAB2 = 13
IDX_INPUT_ENAB3 = 14
IDX_INPUT_ANA = 4
IDX_INPUT_SUP = 15

IDX_OUTPUT_DIG1 = 3
IDX_OUTPUT_DIG2 = 4
IDX_OUTPUT_CC = 5
IDX_OUTPUT_TYPE = 0
IDX_OUTPUT_ANA1 = 1
IDX_OUTPUT_ANA2 = 2
IDX_OUTPUT_ACT = 10
IDX_OUTPUT_ENAB1 = 11
IDX_OUTPUT_ENAB2 = 12
IDX_OUTPUT_ENAB3 = 13

IDX_MOT_LSSTOP = 5
IDX_MOT_LS2START = 6
IDX_MOT_TR = 7
IDX_MOT_STAT = 9
IDX_MOT_TR2 = 17
IDX_MOT_STARTING = 18

IDX_ALARM_IN = 4
IDX_ALARM_ENAB = 7
IDX_ALARM_DISAB = 8
IDX_ALARM_REQACK = 9
IDX_ALARM_ACK = 10
IDX_AXIS_INT: Dict[str, int] = {
    "SUP": 19,
    "INF": 20,
    "ALTFBDIG": 31,
    "HH": 32,
    "H": 33,
    "L": 34,
    "LL": 35,
    "SAFETYUP1": 36,
    "SAFETYUP2": 37,
    "SAFETYUP3": 38,
    "SAFETYUP4": 39,
    "SAFETYUP5": 40,
    "SAFETYUP6": 41,
    "H0": 42,
    "L0": 43,
    # "INDMEM": 44,
    "SAFETYDOWN1": 48,
    "SAFETYDOWN2": 49,
    "SAFETYDOWN3": 50,
    "SAFETYDOWN4": 51,
    "SAFETYDOWN5": 52,
    "SAFETYDOWN6": 53,
    "DECOUPLE1AUTO": 57,
    "DECOUPLE2MAN": 58,
    "DECOUPLE3MAN": 59,
    "DECOUPLE4MAN": 60,
    "DECOUPLE5MAN": 61,
    "DECOUPLE6MAN": 62,
    "FREE70": 70,
    "FREE71": 71,
    "BPDISABLE1": 76,
    "BPDISABLE2": 77,
    "BPDISABLE3": 78,
    "BPDISABLE4": 79,
    "BPDISABLE5": 80,
    "BPDISABLE6": 81,
    "BPDISABLE7": 82,
    "BPDISABLE8": 83,
    "BPDISABLE9": 84,
    "BPDISABLE10": 85,
    "BPDISABLE11": 86,
    "BPDISABLE12": 87,
    "OPTPARAM1": 88,
    "OPTPARAM2": 89,
    "OPTPARAM3": 90,
    "PS1": 63,
    "PS2": 66,
    "PS3": 67,
}
IDX_RCSELAI = 77

IDX_RI_NAME = 0
IDX_RI_CAMPO1 = 6
IDX_RI_CAMPO2 = 7
IDX_RI_ENABLED = 8
IDX_RI_RESET = 12
IDX_RI_IN = 13
IDX_RI_ADDRESS = 5
IDX_RI_IO_INT_ADDR2 = 10

# --- Variabili di sistema: TYPE (IDX_SYSTEM) ---
SYSTEM_TYPE = {
    "INDEX": 0,
    "AXIS": 1,
    "FEEDBACK": 2,
    "INPUT": 3,
    "OUTPUT": 4,
    "MOTOR": 5,
    "PID": 6,
    "TOOLSET": 7,
    "ALARM": 8,
    "MAINT": 9,
    "AXISREAL": 10,
}
SYSTEM_TYPE_REV = {v: k for k, v in SYSTEM_TYPE.items()}

# --- Limiti di indice per ciascun tipo ---
# 48 assi (0..47) per INPUT/OUTPUT/FEEDBACK/AXISREAL
AXIS_MAX_INDEX = 47
INPUT_MAX_INDEX = 47
OUTPUT_MAX_INDEX = 47
FEEDBACK_MAX_INDEX = 47
AXISREAL_MAX_INDEX = 47

# Motori da 1 a 7 (inclusi)
MOTOR_MIN_INDEX = 1
MOTOR_MAX_INDEX = 7

# Toolset 0..7
TOOLSET_MAX_INDEX = 7

# Allarmi 0..191
ALARM_MAX_INDEX = 191

# Manutenzioni 0..31
MAINT_MAX_INDEX = 31

# --- AXIS: gruppi bit con base + indice asse (0->axis[0], 1->axis[1], ...) ---
# Ogni gruppo è distanziato di 64. Dentro al gruppo: base + axis_index
# AXIS_GROUPS_ORDER = [
#     "MOVING", "UP", "DOWN", "MAX", "MIN", "SUPLS", "INFLS",
#     "HH", "H", "L", "LL", "H0", "L0", "SAF", "ALTFB", "BAD",
#     "TILT", "P1UP", "P1DOWN", "P2UP", "P2DOWN", "SLOW", "FAST"
# ]
# AXIS_GROUP_BASE = {name: (2048 + i * 64) for i, name in enumerate(AXIS_GROUPS_ORDER)}
AXIS_GROUP_STEP = 64  # numero max assi per gruppo
BASE_AXIS = 2048


def _build_axis_groups():
    pairs = []
    for name, val in globals().items():
        if name.startswith("IO_SYSAXIS_") and isinstance(val, int) and val >= 0:
            label = name.replace("IO_SYSAXIS_", "")
            pairs.append((label, val))

    pairs.sort(key=lambda lv: lv[1])
    order = [label for label, _ in pairs]
    base = {label: BASE_AXIS + i * AXIS_GROUP_STEP for i, label in enumerate(order)}
    return order, base


AXIS_GROUPS_ORDER, AXIS_GROUP_BASE = _build_axis_groups()

# --- ALARM: campi con base + indice allarme (0..191) ---
# Ogni gruppo è distanziato di 256. Dentro al gruppo: base + alarm_index
ALARM_GROUP_STEP = 256
BASE_ALARM = 16384


def _build_alarm_groups():
    pairs = []
    for name, val in globals().items():
        if name.startswith("IO_SYSALARM_") and isinstance(val, int) and val >= 0:
            label = name.replace("IO_SYSALARM_", "")
            pairs.append((label, val))

    pairs.sort(key=lambda lv: lv[1])
    order = [label for label, _ in pairs]
    base = {label: BASE_ALARM + i * ALARM_GROUP_STEP for i, label in enumerate(order)}
    return order, base


ALARM_GROUPS_ORDER, ALARM_GROUP_BASE = _build_alarm_groups()
