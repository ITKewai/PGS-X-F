#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
from typing import Any, List, Tuple, Optional, Dict
from pathlib import Path
import yaml  # PyYAML
import requests
from urllib3.exceptions import InsecureRequestWarning
import warnings as _warnings

__version__ = "1.0.0"
__author__ = "ITKewai"
__company__ = ""
__product__ = "PSG-X-FindIndex"
__copyright__ = f"Autore: {__author__} © 2025 {__company__}"

# TODO: download config non corrotto,
# TODO: ricerca dei DO, ricerca dei AI, ricerca dei AO
"""
STRUTTURE:
- header: [...]
- ifm:
    - card: [TYPE, DITHERFREQ, DITHERVAL]
    - exc: [EXCTYPE, EXCDITHERFREQ, EXCDITHERVAL]
- axind: [...]
- in: [AUTOSEL, TEACHSEL, CYCLESEL, STARTRESET, REMOTESEL, EMGCYPB, CONSOLE2SEL, CHROLLSEL, x, DEBALNOTPRESS, CONSOLE1SEL, SINGLEMOVSEL, STARTIN, STOPIN, MACSTARTEDIN, HOLDTORUN, RTCOUPLED, RCLEFTSEL, PINCHPRESS, RCRIGHTSEL, STARTSENSORIN, MAINTRESET, MANSEL, TESTSEL, SEMIAUTOSEL, HOLDTORUN2, BPDISABLE1, BPDISABLE2, BPDISABLE3, BPDISABLE4, BPDISABLE5, BPDISABLE6, BPDISABLE7, BPDISABLE8, BPDISABLE9, BPDISABLE10, BPDISABLE11, BPDISABLE12, AUTOMODE, AUTOCYCLEMODE, AUTOSTEPMODE, SEMIAUTOMODE, TEACHMODE, MANMODE, CONSOLE1MODE, CONSOLE2MODE, REMOTEMODE, CHROLLMODE, SINGLEMOVMODE, MACHINESTERTED, x, PUMPONCALC, GREASEALARMCALC, PUMPALARMCALC, x, x, ALARMON, x, ALARMSTOP, MAINTON, RTFWDISABLED, RCLEFTMEM, x, RCRIGHTMEM, HOLDTORUNERROR, x, x, x, MICROSEL, x, QUALITYEND, AUTOSTARTBLINK, QUALITYGOOD, PARTEND, x, PARTBEGIN, x, TILTDISABLED, x, x, x, x, x, x, x, x, x, x, x, x, x, RCV0, RCV1, RCV2, RCV3, RCV4, x, x, x, x, x, x, x, x, x, EMGCYRESETBTN, x, x, INVERTERRESET, INVERTERALARM, AUTOSTARTING, x, x, HOLDTORUNRC, PRELOADUP, PRELOADPINCHDISAB, x, x, x, x, UNBALLEFT, UNBALRIGHT, INVERTEROVERLOAD, LEFTSUPPINTERL, GREASELEVEL, GREASETR, STARTSENSOR2IN, HOLDTORUNRC2, ROLLTILTBALANCED, x, x, x, RIGHTSUPPINTERL, x, x, x]
    per il print:
    AUTOSEL, TEACHSEL, CYCLESEL, REMOTESEL, CONSOLE2SEL, CHROLLSEL, CONSOLE1SEL, SINGLEMOVSEL, MANSEL, TESTSEL, SEMIAUTOSEL, MICROSEL si trovano in config>main>selio
    AUTOMODE, AUTOCYCLEMODE, AUTOSTEPMODE, SEMIAUTOMODE, TEACHMODE, MANMODE, CONSOLE1MODE, CONSOLE2MODE, REMOTEMODE, CHROLLMODE, SINGLEMOVMODE si trovano in config>main>modeio
    DEBALNOTPRESS, MACSTARTEDIN/MACHINESTERTED, ROLLTILTBALANCED, STARTSENSORIN, STARTSENSOR2IN, AUTOSTARTING, AUTOSTARTBLINK, RTFWDISABLED, INVERTERRESET, INVERTERALARM, INVERTEROVERLOAD, LEFTSUPPINTERL, RIGHTSUPPINTERL si trovano in config>main>statusio
    STARTRESET, STARTIN, STOPIN, MAINTRESET, UNBALLEFT, UNBALRIGHT, TILTDISABLED si trovano in config>main>cmdio
    MACHINESTARTED, ALARMON, ALARMSTOP, MAINTON, QUALITYEND, QUALITYGOOD, PARTEND, PARTBEGIN si trovano in config>main>rsmio
    EMGCYRESETBTN, EMGCYPB, HOLDTORUN, HOLDTORUN2, HOLDTORUNRC, HOLDTORUNRC2, HOLDTORUNERROR si trovano in config>safety
    PINCHPRESS, PRELOADUP, PRELOADPINCHDISAB si trovano in config>pinchpreload
    RTCOUPLED si trova in config>rt
    BPDISABLE* si trovano in config>bp
    PUMPONCALC, GREASEALARMCALC, PUMPALARMCALC, GREASETR, GREASELEVEL si trovano in config>grease
    RCV* (0..4), RCLEFTSEL, RCRIGHTSEL, RCLEFTMEM, RCRIGHTMEM si trovano in config>radiocontrol
- out: ["x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","MACSTARTLIGHT_DO","x","x","x","x","MACREADYLIGHT_DO","x","x","STARTCMD_DO","x","x","x","x","STOPCMD_DO","x","x","x","x","x","x","x","x","x","x","EYEBENDON_DO","BP1_DO","BP2_DO","BP3_DO","BP4_DO","BP5_DO","BP6_DO","BP7_DO","BP8_DO","BP9_DO","BP10_DO","BP11_DO","BP12_DO","x","x","x","x","x","RCUM_DO","RCLEFTUP_DO","RCLEFTDOWN_DO","RCRIGHTUP_DO","RCRIGHTDOWN_DO","RCBOTTONUP_DO","RCBOTTOMDOWN_DO","RCTOPLEFT_DO","RCTOPRIGHT_DO","RCALARM_DO","EMGCYRESETBTN_DO","EMGCYRESETLIGHT_DO","x","PINCHPRESSAR_DO","PINCHPRESSAR2_DO","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x"]
    per il print
    MACSTARTLIGHT_DO, MACREADYLIGHT_DO, STARTCMD_DO, STOPCMD_DO  si trovano in config>main>cmdio
    EMGCYRESETLIGHT_DO, EMGCYRESETBTN_DO  si trovano in config>safety
    PINCHPRESSAR_DO, PINCHPRESSAR2_DO si trovano in config>pinchprelaod
    BP*_DO si trovano in config>bp
    EYEBEND_DO si trova in config>checkmeasurement
    RCUM_DO, RCLEFTUP_DO,RCLEFTDOWN_DO,RCRIGHTUP_DO,RCRIGHTDOWN_DO,RCBOTTOMUP_DO,RCBOTTOMDOWN_DO,RCTOPLEFT_DO,RCTOPRIGHT_DO,RCALARM_DO si trovano in config>radiocontrol>in
    
- param:
    - pstring: [MODEL, COSTUMER,x,x]
    - pbool: [...]
    - pint: [COMMESSA,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x]
    - preal: [...]
    - ptype: [...]
- io:
    - di: [NAME, BOOL_DEFAULT_VALUE, x, SIM, BOOL_SIM_VALUE, ADDRESS, CAMPO_1, CAMPO_2, x, UM, MEMTYPE, MEMIND, TIMEOUT, IN, x, x, x, x, x, EXPRTYPE, EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR, EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR, EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR, EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR, EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR, EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR]
        (EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR) si attivano se EXPRTYPE != -1 se no non ci sono proprio
    - ai: [NAME, BOOL_DEFAULT_VALUE, x, SIM, BOOL_SIM_VALUE, ADDRESS, CAMPO_1, CAMPO_2, NBYTES, UM, MEMTYPE, MEMIND, TIMEOUT, IN, DINTDEFAULTVALUE, DINTSIMVALUE, DEADBAND, x, TOTDELTAMAX, COEFFMULT, x]
    - ao: [NAME, BOOL_DEFAULT_VALUE, PROG, SIM, BOOL_SIM_VALUE, ADDRESS, CAMPO_1, CAMPO_2, NBYTES, UM, MEMTYPE, MEMIND, IN, AODUAL, DINTDEFAULTVALUE, DINTSIMVALUE, x, x, x, AOPRIORITY, x]
    - do: [NAME, BOOL_DEFAULT_VALUE, x, SIM, BOOL_SIM_VALUE, ADDRESS, CAMPO_1, CAMPO_2, x, UM, MEMTYPE, MEMIND, TIMEOUT, IN, x, x, x, x, x, x,x]
    - ri: [...]
- obj:
    - axis: [NAME]
        bool: [x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x]
        int: ["x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","x","SUP","INF","x","x","x","x","x","x","x","x","x","x","ALTFBDIG","HH","H","L","LL","SAFETYUP1","SAFETYUP2","SAFETYUP3","SAFETYUP4","SAFETYUP5","SAFETYUP6","H0","L0","x","x","x","x","x","x","x","x","SAFETYDOWN1","SAFETYDOWN2","SAFETYDOWN3","SAFETYDOWN4","SAFETYDOWN5","SAFETYDOWN6","x","x","x","DECOUPLE1AUTO","DECOUPLE2MAN","DECOUPLE3MAN","DECOUPLE4MAN","DECOUPLE5MAN","DECOUPLE6MAN","PS1","x","x","PS2","PS3","x","x","x","x","x","FREE70","FREE71","x","x","x","x","x","x","x","BPDISABLE1","BPDISABLE2","BPDISABLE3","BPDISABLE4","BPDISABLE5","BPDISABLE6","BPDISABLE7","BPDISABLE8","BPDISABLE9","BPDISABLE10","BPDISABLE11","BPDISABLE12","OPTPARAM1","OPTPARAM2","OPTPARAM3"]
        type: [x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x]
    - input: [HOLDTORUNENAB,x,INPUT_TYPE,INPUT_MESURETYPE, ANA, DIGUP1, DIGDOWN1, K, DIGUP2, DIGDOWN2, K2, ACT, ENAB1, ENAB2, ENAB3, SUP, SEQ, VMIN, VMAX, VMIN2, VMAX2]
    - fb: [FB_TYPE, FB_MESURETYPE, RESETIND, ININD, FB_ERR_DEPRECATED, INFUNDERFLOW, SUPOVERFLOW, DEADBAND, RATIO, x, x]
    - output: [OUTPUT_TYPE, ANA1, ANA2, DIG1, DIG2, CC, RPM, TIMEOUTBRKADV,ADVDEFSIDE,FREE,ACT,ENAB1,ENAB2,ENAB3, SCALEMIN1, SCALEMAX1, SCALEMIN2, SCALEMAX2, SCALEMIN1H, SCALEMAX1H, SCALEMIN2H, SCALEMAX2H, VALMIN1, VALMAX1, VALMIN2, VALMAX2, VIN0, VOUT0, VIN1, VOUT1, VIN2, VOUT2, VIN3, VOUT3, VIN4, VOUT4, VIN5, VOUT5, V2IN0, V2OUT0, V2IN1, V2OUT1, V2IN2, V2OUT2, V2IN3, V2OUT3, V2IN4, V2OUT4, V2IN5, V2OUT5] 
        se OUTPUT_TYPE = ADV
        ANA1 = ADVIND
        ANA2 = ADVSTART
        DIG1 = ADVENABLE
        DIG2 = BRAKE
        se OUTPUT_TYPE = PSLCAN
        RPM = CTRL1PSLCAN
        TIMEOUTBRKADV = STATUS1PSLCAN
        ADVDEFSIDE = CTRL2PSLCAN
        FREE = STATUS2PSLCAN  
        se OUTPUT_TYPE = ATV340
        RPM = RPMATV
        se OUTPUT_TYPE = SELSLOW
        ANA1 = DIG1ADD
        ANA2 = DIG2ADD
    - mot: [CONFIG, SELECTABLE, SEQ, OPT, DEFAULT, LSSTOP,LS2START, TR, CMD, STAT, TIMEOUT, CMD1, CMD2, CMD3, TIMEOUT2, MOT_TYPE, TIMEOUTBTN, TR2, STARTING]
    - alarm: [NAME,CONFIG,INVOUT,MODE,IN,OUT,COD,ENAB,DISAB,REQACK,ACK,TIMEOUT, FREE]
    - maint [...] TODO: ci sono in e out da cercare poi
"""

"""
Variabili di sistema
TYPE: (IDX_SYSTEM)
    INDEX = 1
    AXIS = 2
    FEEDBACK = 3
    INPUT = 4
    OUTPUT = 5
    MOTOR = 6
    PID = 7
    TOOLSET = 8
    ALARM = 9
    MAINT = 10
    AXISREAL = 11
in base al tipo partendo da 0 che è axis[0] e incrementando
AXIS: 
    MOVING (2048=0, 2049=1, ...)
    UP (2112=0, ...)
    DOWN (2176=0, ...)
    MAX (2240=0, ...)
    MIN (2304=0, ...)
    SUPLS (2368=0, ...)
    INFLS (2432=0, ...)
    HH (2496=0, ...)
    H (2560=0, ...)
    L (2624=0, ...)
    LL (2688=0, ...)
    H0 (2752=0, ...)
    L0 (2816=0, ...)
    SAF (2880=0, ...)
    ALTFB (2944=0, ...)
    BAD (3008=0, ...)
    TILT (3072=0, ...)
    P1UP (3136=0, ...)
    P1DOWN (3200=0, ...)
    P2UP (3264=0, ...)
    P2DOWN (3328=0, ...)
    SLOW (3392=0, ...)
    FAST (3456=0, ...)
FEEDBACK:
    ERR
    RESET
INPUT:
    ACT
    ENAB1
    ENAB2
    ENAB3
    ENAB
OUTPUT:
    ACT
    ENAB1
    ENAB2
    ENAB3
    ENAB
MOTOR:
    STAT
    CMD
    STOP
    START
    TR
    TR2
    CMD1
    CMD2
    CMD3
    STARTING
    SEL
    SEQ
    OPT
    DEF
TOOLSET:
    SELECTED
ALARM:
    VAL (16384=0, ..)
    ENAB (16640=0, ..)
    DISAB (16896=0, ..)
    REQ (17152=0, ..)
    ACK (17408=0, ..)
    IN (17664=0, ..)
MAINT:
    VAL
    ENAB
    DISAB
AXISREAL:
    POS
    SPEED
    DELTA
    SUP
"""
'''
NOTE: dentro gli -ao se tipo = PNET o CAN, trovo in IN e AO_DUAL gli -ai
'''

# --- Mappe fornite ---
ADDRESS = {
    -1: '',
    0: 'PNET',
    1: 'CAN',
    2: 'SW',
    3: 'CALC',
    4: 'TOT',
    5: 'TOTAUTO',
    6: 'TOTMAN',
    7: 'DAILYTOT',
    8: 'DAILYTOTAUTO',
    9: 'DAILYTOTMAN',
    10: 'TIME',
    11: 'TIMEAUTO',
    12: 'TIMEMAN',
    13: 'DAILYTIME',
    14: 'DAILYTIMEAUTO',
    15: 'DAILYTIMEMAN',
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

# SOLO SE ADDRESS >= 4
CAMPO_1 = {
    -1: '',
    0: 'DI',
    1: 'AI',
    2: 'DO',
    3: 'AO',
    4: 'RI',
}

EXPRTYPE = {
    -1: '',
    0: 'CYCLE',
    1: 'TRIGGER',
}

INPUT_MESURETYPE = UM.copy()

OUTPUT_TYPE = {
    -1: '',
    0: 'SEL',
    1: 'DIR',
    2: 'DIRINV',
    3: 'SELSLOW',
    4: 'ADV',
    5: 'PSLCAN',
    6: 'SELFL',
    7: 'SEL2PV',
    8: 'ATV340',
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
IDX_FB_ERR_DEPRECATED = 4
DI_NUM_EXPR_GROUPS = 8
DI_EXPR_GROUP_SIZE = 3  # (EXPR_OPERAND, EXPR_ADDRESS, EXPR_OPERATOR)
IDX_INPUT_DIGUP1 = 5
IDX_INPUT_DIGDOWN1 = 6
IDX_INPUT_DIGUP2 = 8
IDX_INPUT_DIGDOWN2 = 9
IDX_INPUT_ACT = 11
IDX_INPUT_ENAB1 = 12
IDX_INPUT_ENAB2 = 13
IDX_INPUT_ENAB3 = 14
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

# --- Variabili di sistema: TYPE (IDX_SYSTEM) ---
SYSTEM_TYPE = {
    "INDEX": 1,
    "AXIS": 2,
    "FEEDBACK": 3,
    "INPUT": 4,
    "OUTPUT": 5,
    "MOTOR": 6,
    "PID": 7,
    "TOOLSET": 8,
    "ALARM": 9,
    "MAINT": 10,
    "AXISREAL": 11,
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
AXIS_GROUPS_ORDER = [
    "MOVING", "UP", "DOWN", "MAX", "MIN", "SUPLS", "INFLS",
    "HH", "H", "L", "LL", "H0", "L0", "SAF", "ALTFB", "BAD",
    "TILT", "P1UP", "P1DOWN", "P2UP", "P2DOWN", "SLOW", "FAST"
]
AXIS_GROUP_BASE = {name: (2048 + i * 64) for i, name in enumerate(AXIS_GROUPS_ORDER)}
AXIS_GROUP_STEP = 64  # numero max assi per gruppo

# --- ALARM: campi con base + indice allarme (0..191) ---
# Ogni gruppo è distanziato di 256. Dentro al gruppo: base + alarm_index
ALARM_GROUPS_ORDER = ["VAL", "ENAB", "DISAB", "REQ", "ACK", "IN"]
ALARM_GROUP_BASE = {name: (16384 + i * 256) for i, name in enumerate(ALARM_GROUPS_ORDER)}
ALARM_GROUP_STEP = 256


# ---- Funzioni AXIS ----
def make_axis_sys_addr(group: str, axis_index: int) -> int:
    g = group.strip().upper()
    if g not in AXIS_GROUP_BASE:
        raise KeyError(f"Gruppo AXIS sconosciuto: {group}")
    if not (0 <= axis_index <= AXIS_MAX_INDEX):  # 0..47
        raise ValueError(f"axis_index fuori range (0..{AXIS_MAX_INDEX}): {axis_index}")
    return AXIS_GROUP_BASE[g] + axis_index


def parse_axis_sys_addr(addr: int) -> Optional[Tuple[str, int]]:
    if addr < 2048 or addr >= 2048 + AXIS_GROUP_STEP * len(AXIS_GROUPS_ORDER):
        return None
    group_idx = (addr - 2048) // AXIS_GROUP_STEP
    if not (0 <= group_idx < len(AXIS_GROUPS_ORDER)):
        return None
    base = 2048 + group_idx * AXIS_GROUP_STEP
    axis_index = addr - base
    if not (0 <= axis_index <= AXIS_MAX_INDEX):  # 0..47
        return None
    return (AXIS_GROUPS_ORDER[group_idx], axis_index)


def make_alarm_sys_addr(group: str, alarm_index: int) -> int:
    g = group.strip().upper()
    if g not in ALARM_GROUP_BASE:
        raise KeyError(f"Gruppo ALARM sconosciuto: {group}")
    if not (0 <= alarm_index <= ALARM_MAX_INDEX):  # 0..191
        raise ValueError(f"alarm_index fuori range (0..{ALARM_MAX_INDEX}): {alarm_index}")
    return ALARM_GROUP_BASE[g] + alarm_index


def parse_alarm_sys_addr(addr: int) -> Optional[Tuple[str, int]]:
    if addr < 16384 or addr >= 16384 + ALARM_GROUP_STEP * len(ALARM_GROUPS_ORDER):
        return None
    group_idx = (addr - 16384) // ALARM_GROUP_STEP
    if not (0 <= group_idx < len(ALARM_GROUPS_ORDER)):
        return None
    base = 16384 + group_idx * ALARM_GROUP_STEP
    alarm_index = addr - base
    if not (0 <= alarm_index <= ALARM_MAX_INDEX):  # 0..191
        return None
    return (ALARM_GROUPS_ORDER[group_idx], alarm_index)


# ---- Decoder generale (AXIS / ALARM; altri tipi in futuro) ----
def decode_system_addr(addr: int) -> Optional[str]:
    """
    Prova a decodificare un indirizzo di sistema in forma umana.
    Ritorna stringa tipo 'AXIS.MOVING[3]' oppure 'ALARM.ACK[12]' oppure None.
    """
    ax = parse_axis_sys_addr(addr)
    if ax:
        g, i = ax
        return f"AXIS.{g}[{i}]"
    al = parse_alarm_sys_addr(addr)
    if al:
        g, i = al
        return f"ALARM.{g}[{i}]"
    return None


def validate_system_index(sys_type: str, index: int) -> None:
    """Lancia ValueError se l'indice non rientra nei limiti dichiarati per il tipo."""
    t = sys_type.strip().upper()
    if t in {"AXIS", "INPUT", "OUTPUT", "FEEDBACK", "AXISREAL"}:
        if not (0 <= index <= AXIS_MAX_INDEX):
            raise ValueError(f"{t} index fuori range (0..{AXIS_MAX_INDEX}): {index}")
    elif t == "MOTOR":
        if not (MOTOR_MIN_INDEX <= index <= MOTOR_MAX_INDEX):
            raise ValueError(f"MOTOR index fuori range ({MOTOR_MIN_INDEX}..{MOTOR_MAX_INDEX}): {index}")
    elif t == "TOOLSET":
        if not (0 <= index <= TOOLSET_MAX_INDEX):
            raise ValueError(f"TOOLSET index fuori range (0..{TOOLSET_MAX_INDEX}): {index}")
    elif t == "ALARM":
        if not (0 <= index <= ALARM_MAX_INDEX):
            raise ValueError(f"ALARM index fuori range (0..{ALARM_MAX_INDEX}): {index}")
    elif t == "MAINT":
        if not (0 <= index <= MAINT_MAX_INDEX):
            raise ValueError(f"MAINT index fuori range (0..{MAINT_MAX_INDEX}): {index}")
    else:
        raise ValueError(f"Tipo di sistema sconosciuto: {sys_type}")


def sysref(sys_type: str, field: str, index: int) -> str:
    """
    Ritorna una stringa tipo 'AXIS.MOVING[3]' o 'ALARM.ACK[12]'.
    Per gli altri tipi valida il range e usa lo stesso formato 'TIPO.CAMPO[idx]'.
    """
    t = sys_type.strip().upper()
    f = field.strip().upper()
    validate_system_index(t, index)

    if t == "AXIS":
        if f not in AXIS_GROUP_BASE:
            raise KeyError(f"Campo AXIS sconosciuto: {field}")
        return f"AXIS.{f}[{index}]"

    if t == "ALARM":
        if f not in ALARM_GROUP_BASE:
            raise KeyError(f"Campo ALARM sconosciuto: {field}")
        return f"ALARM.{f}[{index}]"

    # altri tipi (INPUT/OUTPUT/FEEDBACK/MOTOR/TOOLSET/MAINT/AXISREAL)
    return f"{t}.{f}[{index}]"


# --- END SYSTEM LOGIC

def _sanitize_yaml_like(text: str) -> str:
    """
    Converte sequenze in stile YAML con elementi vuoti/trailing comma in 'null'.
    Esempi:
      [a, b,,]   -> [a, b, null, null]
      [,a,,b,]   -> [null, a, null, b, null]
    NOTE: approccio best-effort basato su regex; pensato per casi reali del file.
    """
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r',\s*,', ', null,', text)  # elemento vuoto tra due virgole
    text = re.sub(r'\[\s*,', '[ null,', text)  # vuoto subito dopo '['
    text = re.sub(r',\s*\]', ', null]', text)  # vuoto prima di ']'
    return text


def get_run_dir() -> Path:
    """
    Ritorna la cartella di riferimento per i file esterni.
    - Se il programma è 'frozen' (PyInstaller), usa la cartella dell'eseguibile.
    - Altrimenti usa la cartella del file sorgente.
    """
    if getattr(sys, 'frozen', False):
        # es. C:\cartella\del\tuo\programma (dove risiede .exe)
        return Path(sys.executable).resolve().parent
    # esecuzione da sorgente
    return Path(__file__).resolve().parent


def load_yaml(path: str) -> Any:
    text = Path(path).read_text(encoding='utf-8')
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        text2 = _sanitize_yaml_like(text)
        try:
            data = yaml.safe_load(text2)
        except yaml.YAMLError as e1:
            text3 = _sanitize_pstring_flow_lists(text2)
            try:
                data = yaml.safe_load(text3)
            except yaml.YAMLError as e2:
                raise RuntimeError("Config YAML non leggibile dopo i tentativi di sanificazione.") from e2

    # ---- raggruppa IO e impacchetta i DI per indice di canale ----
    io_grouped = _group_io(data.get('io'))
    io_grouped['di'] = _pack_by_index(io_grouped.get('di', []), idx_pos=7)
    data['io'] = io_grouped
    # Raggruppa gli oggetti (fb) sotto 'obj'
    obj_grouped = _group_obj(data.get('obj'))
    data['obj'] = obj_grouped
    return data


def _sanitize_pstring_flow_lists(text: str) -> str:
    """
    Converte pstring: [a,b,,] -> pstring: ['a', 'b', null, null]
    (solo per le righe 'pstring', non tocca il resto)
    """

    def fix(match: re.Match) -> str:
        indent = match.group(1) or ""
        inner = match.group(2) or ""
        tokens = [t.strip() for t in inner.split(",")]
        out = []
        for t in tokens:
            if t == "" or t.lower() in {"none", "null"}:
                out.append("null")
            else:
                # se contiene spazi e non è già quotato, quota
                if not (t.startswith("'") and t.endswith("'")) and not (t.startswith('"') and t.endswith('"')):
                    if " " in t:
                        t = "'" + t.replace("'", "''") + "'"
                out.append(t)
        return f"{indent}pstring: [{', '.join(out)}]"

    # solo righe pstring in stile flow
    return re.sub(r"(?mi)^(\s*)pstring\s*:\s*\[(.*?)\]\s*$", fix, text)


def _group_io(io_node: Any, keys=('di', 'ai', 'do', 'ao', 'ri', 'fb')) -> Dict[str, List[list]]:
    grouped: Dict[str, List[list]] = {k: [] for k in keys}

    def _is_row(x: Any) -> bool:
        return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)

    if isinstance(io_node, list):
        for item in io_node:
            if isinstance(item, dict) and len(item) == 1:
                k, v = next(iter(item.items()))
                kl = str(k).lower()
                if kl in grouped:
                    if _is_row(v):
                        grouped[kl].append(v)
                    elif isinstance(v, list):
                        grouped[kl].extend([el for el in v if _is_row(el)])
    elif isinstance(io_node, dict):
        for k, v in io_node.items():
            kl = str(k).lower()
            if kl in grouped:
                if _is_row(v):
                    grouped[kl].append(v)
                elif isinstance(v, list):
                    grouped[kl].extend([el for el in v if _is_row(el)])
    return grouped


def _group_obj(obj_node: Any) -> Dict[str, List[list] | List[dict]]:
    """
    Raggruppa fb/input/output/mot/alarm come liste di righe e PRESERVA i blocchi 'axis'
    (dict che contengono almeno la chiave 'axis' e tipicamente anche 'int','bool','type').
    Ritorna:
      {
        'fb': [...],
        'input': [...],
        'output': [...],
        'mot': [...],
        'alarm': [...],
        'axis': [ { 'axis': [...], 'int': [...], 'bool': [...], 'type': [...] }, ... ]
      }
    """
    grouped: Dict[str, List[list] | List[dict]] = {
        'fb': [],
        'input': [],
        'output': [],
        'mot': [],
        'alarm': [],
        'axis': [],
    }

    def _is_row(x: Any) -> bool:
        return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            # Se è un blocco axis (ha la chiave 'axis'), lo conserviamo intero
            if 'axis' in node and isinstance(node.get('axis'), list):
                grouped['axis'].append(node)
            # Raggruppa chiavi note se in forma semplice
            for k, v in node.items():
                kl = str(k).lower()
                if kl in ('fb', 'input', 'output', 'mot', 'alarm'):  # <--- alarm incluso
                    if _is_row(v):
                        grouped[kl].append(v)  # es. {'fb': [ ...campi... ]}
                    elif isinstance(v, list):
                        grouped[kl].extend([el for el in v if _is_row(el)])  # es. {'fb': [[...],[...]]}
                # Scendi ricorsivamente per trovare altri blocchi/righe
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(obj_node)
    return grouped


def _pack_by_index(rows: List[list], idx_pos: int = 7) -> List[Optional[list]]:
    indexed: Dict[int, list] = {}
    extras: List[list] = []
    for r in rows:
        idx = r[idx_pos] if isinstance(r, list) and len(r) > idx_pos and isinstance(r[idx_pos], int) and r[
            idx_pos] >= 0 else None
        if idx is None:
            extras.append(r)
        elif idx not in indexed:
            indexed[idx] = r
        else:
            extras.append(r)
    if not indexed:
        return rows
    packed: List[Optional[list]] = [None] * (max(indexed.keys()) + 1)
    for i, r in indexed.items():
        packed[i] = r
    packed.extend(extras)
    return packed


def find_section(root: Any, keys: List[str]) -> Optional[List[list]]:
    """
    Cerca ricorsivamente tutte le occorrenze di chiavi in `keys` (case-insensitive)
    in qualunque punto della struttura (dict o list). Ogni valore trovato che sia
    una LISTA 'riga' (es. un singolo DI) viene aggiunto al risultato.
    Se il valore è una lista di liste, le appiattisce.
    Restituisce una lista di liste oppure None se non trova nulla.
    """
    targets = {k.lower() for k in keys}
    found: List[list] = []

    def is_row(x: Any) -> bool:
        # una "riga" è una lista i cui elementi NON sono dict/list annidati
        return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                # se la chiave è tra quelle cercate, prova a raccogliere il valore
                if k.lower() in targets:
                    if is_row(v):
                        found.append(v)  # es. {'di': [ ... campi ... ]}
                    elif isinstance(v, list):
                        # potrebbe essere una lista di righe: [[...],[...],...]
                        rows = [list(el) for el in v if is_row(el)]
                        if rows:
                            found.extend(rows)
                # continua a scendere comunque
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(root)
    return found or None


def get_commessa_from_param(data: Any) -> Optional[str]:
    """
    Ritorna la stringa della commessa da param.pint[0], se presente.
    Supporta sia:
      - param: { pint: [COMMESSA, ...] }
      - param: [ { pint: [COMMESSA, ...] }, ... ]
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


def _find_axis_int_lists(root: Any) -> List[List[Any]]:
    """
    Ritorna tutte le liste 'int' appartenenti a nodi 'axis'.
    Un nodo 'axis' è un dict che contiene la chiave 'axis' (es. 'axis': [NAME])
    e a fianco una chiave 'int' che è una lista di interi.
    """
    axis_ints: List[List[Any]] = []

    def walk(node: Any, under_axis: bool = False) -> None:
        if isinstance(node, dict):
            # un livello è "axis" se ha la chiave 'axis' (come da struttura mostrata)
            is_axis_here = under_axis or ('axis' in node and isinstance(node.get('axis'), list))
            # se siamo su un livello axis e troviamo 'int' come lista, raccogliamo
            if is_axis_here and isinstance(node.get('int'), list):
                axis_ints.append(node['int'])
            # continua discesa
            for k, v in node.items():
                walk(v, under_axis=is_axis_here or (k == 'axis'))
        elif isinstance(node, list):
            for item in node:
                walk(item, under_axis=under_axis)

    walk(root, under_axis=False)
    return axis_ints


def iter_expr_groups(di_fields: list) -> List[Tuple[int, int, int]]:
    groups: List[Tuple[int, int, int]] = []
    if not isinstance(di_fields, list) or len(di_fields) <= IDX_EXPRTYPE:
        return groups
    # EXPRTYPE è a indice 20; le terne partono da 21 → (operand, address, operator)
    start = IDX_EXPRTYPE + 1
    max_needed = start + DI_NUM_EXPR_GROUPS * DI_EXPR_GROUP_SIZE
    limit = min(len(di_fields), max_needed)
    i = start
    while i + 2 < limit and len(groups) < DI_NUM_EXPR_GROUPS:
        try:
            operand = int(di_fields[i])
        except Exception:
            operand = -999999
        try:
            address = int(di_fields[i + 1])
        except Exception:
            address = -999999
        try:
            operator = int(di_fields[i + 2])
        except Exception:
            operator = -999999
        groups.append((operand, address, operator))  # (OPERAND, ADDRESS, OPERATOR)
        i += DI_EXPR_GROUP_SIZE
    return groups


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
    axis_int_lists = _find_axis_int_lists(data.get('obj'))
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


def get_axis_int_di(data: Any, axis_index: int, label: str) -> Optional[int]:
    """Ritorna il DI configurato nell'array AXIS.INT per l'asse e la label dati."""
    axis_nodes = ((data.get('obj') or {}).get('axis') or [])
    try:
        node = axis_nodes[axis_index]
        arr = node.get('int')
        if not isinstance(arr, list):
            return None
        pos = IDX_AXIS_INT[label.strip().upper()]
        val = arr[pos]
        return int(val) if val is not None and str(val).strip() != '' else None
    except Exception:
        return None


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


def search_ai_in_ao_matches(ao_list: List[list], target_number: int, only_bus: bool = True) -> List[
    Tuple[int, str, Optional[str]]]:
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


def search_fb_err_deprecated_matches(fb_list: List[list], target_number: int) -> List[Tuple[int, Optional[str]]]:
    """
    Cerca tutti i FB che hanno il campo FB_ERR_DEPRECATED (indice 4) uguale a target_number.
    Ritorna: [(indice_fb, fb_type_string_opzionale)]
    """
    results: List[Tuple[int, Optional[str]]] = []
    for fb_index, fb_fields in enumerate(fb_list or []):
        if not isinstance(fb_fields, list) or len(fb_fields) <= IDX_FB_ERR_DEPRECATED:
            continue
        try:
            err_val = int(fb_fields[IDX_FB_ERR_DEPRECATED])
        except Exception:
            continue
        if err_val == target_number:
            fb_type_str: Optional[str] = None
            if len(fb_fields) > IDX_FB_TYPE:
                try:
                    fb_type_val = int(fb_fields[IDX_FB_TYPE])
                except Exception:
                    fb_type_val = -1
                fb_type_str = FB_TYPE.get(fb_type_val, str(fb_type_val))
            results.append((fb_index, fb_type_str))
    return results


def search_fb_resetind_matches(fb_list: List[list], target_number: int) -> List[Tuple[int, Optional[str]]]:
    """
    Cerca tutti i FB che hanno il campo RESETIND (indice 2) uguale a target_number.
    Ritorna: [(indice_fb, fb_type_string_opzionale)]
    """
    results: List[Tuple[int, Optional[str]]] = []
    for fb_index, fb_fields in enumerate(fb_list or []):
        if not isinstance(fb_fields, list) or len(fb_fields) <= IDX_FB_RESETIND:
            continue
        try:
            reset_val = int(fb_fields[IDX_FB_RESETIND])
        except Exception:
            continue
        if reset_val == target_number:
            fb_type_str: Optional[str] = None
            if len(fb_fields) > IDX_FB_TYPE:
                try:
                    fb_type_val = int(fb_fields[IDX_FB_TYPE])
                except Exception:
                    fb_type_val = -1
                fb_type_str = FB_TYPE.get(fb_type_val, str(fb_type_val))
            results.append((fb_index, fb_type_str))
    return results


def search_input_di_field_matches(input_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in obj>input i campi DIGUP1, DIGDOWN1, DIGUP2, DIGDOWN2, ENAB1, ENAB2, ENAB3
    che referenziano il DI `target_number`.
    Ritorna: [(indice_input, [nomi_campi_match])]
    """
    results: List[Tuple[int, List[str]]] = []
    fields = [
        ("DIGUP1", IDX_INPUT_DIGUP1),
        ("DIGDOWN1", IDX_INPUT_DIGDOWN1),
        ("DIGUP2", IDX_INPUT_DIGUP2),
        ("DIGDOWN2", IDX_INPUT_DIGDOWN2),
        ("ACT", IDX_INPUT_ACT),
        ("ENAB1", IDX_INPUT_ENAB1),
        ("ENAB2", IDX_INPUT_ENAB2),
        ("ENAB3", IDX_INPUT_ENAB3),
    ]
    for inp_index, inp_fields in enumerate(input_list or []):
        if not isinstance(inp_fields, list):
            continue
        matched: List[str] = []
        for label, idx in fields:
            if len(inp_fields) > idx:
                try:
                    val = int(inp_fields[idx])
                except Exception:
                    continue
                if val == target_number:
                    matched.append(label)
        if matched:
            results.append((inp_index, matched))
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


def search_mot_di_field_matches(mot_list: List[list], target_number: int) -> List[Tuple[int, List[str]]]:
    """
    Cerca in obj>mot i campi LSSTOP, LS2START, TR, STAT, TR2, STARTING
    che referenziano il DI `target_number`.
    Ritorna: [(indice_mot, [nomi_campi_match])]
    """
    results: List[Tuple[int, List[str]]] = []
    field_specs = [
        ("LSSTOP", IDX_MOT_LSSTOP),
        ("LS2START", IDX_MOT_LS2START),
        ("TR", IDX_MOT_TR),
        ("STAT", IDX_MOT_STAT),
        ("TR2", IDX_MOT_TR2),  # "T2"
        ("STARTING", IDX_MOT_STARTING),
    ]

    for mot_index, mot_fields in enumerate(mot_list or []):
        if not isinstance(mot_fields, list):
            continue
        matched: List[str] = []
        for label, idx in field_specs:
            if len(mot_fields) > idx:
                try:
                    val = int(mot_fields[idx])
                except Exception:
                    continue
                if val == target_number:
                    matched.append(label)
        if matched:
            results.append((mot_index, matched))

    return results


def search_alarm_di_field_matches(alarm_list: List[list], target_number: int) -> List[
    Tuple[int, List[str], Optional[str]]]:
    """
    Cerca nei -obj.alarm i campi IN, ENAB, DISAB, REQACK, ACK che referenziano il DI `target_number`.
    Ritorna: [(indice_alarm, [nomi_campi_match], nome_alarm opz.)]
    """
    results: List[Tuple[int, List[str], Optional[str]]] = []
    fields = [
        ("IN", IDX_ALARM_IN),
        ("ENAB", IDX_ALARM_ENAB),
        ("DISAB", IDX_ALARM_DISAB),
        ("REQACK", IDX_ALARM_REQACK),
        ("ACK", IDX_ALARM_ACK),
    ]
    for alarm_idx, alarm_fields in enumerate(alarm_list or []):
        if not isinstance(alarm_fields, list):
            continue
        matched: List[str] = []
        for label, idx in fields:
            if len(alarm_fields) > idx:
                try:
                    val = int(alarm_fields[idx])
                except Exception:
                    continue
                if val == target_number:
                    matched.append(label)
        if matched:
            name: Optional[str] = None
            if len(alarm_fields) > 0 and isinstance(alarm_fields[0], (str, int, float)):
                name = str(alarm_fields[0])
            results.append((alarm_idx, matched, name))
    return results


def search_axis_int_di_field_matches(axis_int_lists: List[List[Any]], target_number: int) -> List[
    Tuple[int, List[str]]]:
    """
    Cerca in ciascun array 'axis.int' i campi etichettati (SUP, INF, ALTFBDIG, HH, H, L, LL,
    SAFETYUP1..6, H0, L0, INDMEM, SAFETYDOWN1..6, DECOUPLE1AUTO..6, FREE70, FREE71,
    BPDISABLE1..12, OPTPARAM1..3) che referenziano il DI 'target_number'.
    Ritorna: [(indice_axis, [nomi_campi_match])]
    """
    results: List[Tuple[int, List[str]]] = []
    for axis_idx, arr in enumerate(axis_int_lists or []):
        if not isinstance(arr, list):
            continue
        matched: List[str] = []
        for label, idx in IDX_AXIS_INT.items():
            if idx < 0:
                continue
            if idx >= len(arr):
                continue
            try:
                val = int(arr[idx])
            except Exception:
                continue
            if val == target_number:
                matched.append(label)
        if matched:
            results.append((axis_idx, matched))
    return results


# ---- Ricerca nei campi -in ---------------------------------------------------

def _find_in_arrays(root: Any) -> List[List[Any]]:
    """Raccoglie tutte le liste associate alla chiave 'in' in obj."""
    return find_section(root, ['in']) or []


def _is_mostly_ints(arr: List[Any]) -> bool:
    ints = 0
    for v in arr:
        try:
            if isinstance(v, bool):
                continue
            int(v)  # prova cast
            ints += 1
        except Exception:
            pass
    return ints >= max(1, len(arr) // 2)


def _is_mostly_strings(arr: List[Any]) -> bool:
    strings = sum(1 for v in arr if isinstance(v, str))
    return strings >= max(1, len(arr) // 2)


# Mappa (grezza) label -> "origine" per le stampe
_IN_ORIGIN_SETS = {
    "config>main>selio": {
        "AUTOSEL", "TEACHSEL", "CYCLESEL", "REMOTESEL", "CONSOLE2SEL", "CHROLLSEL",
        "CONSOLE1SEL", "SINGLEMOVSEL", "MANSEL", "TESTSEL", "SEMIAUTOSEL", "MICROSEL"
    },
    "config>main>modeio": {
        "AUTOMODE", "AUTOCYCLEMODE", "AUTOSTEPMODE", "SEMIAUTOMODE", "TEACHMODE", "MANMODE",
        "CONSOLE1MODE", "CONSOLE2MODE", "REMOTEMODE", "CHROLLMODE", "SINGMOBMODE", "SINGLEMOVMODE"
    },
    "config>main>statusio": {
        "DEBALNOTPRESS", "MACSTERTEDIN", "ROLLTILTBALANCED", "STARTSENSORIN", "STARTSENSOR2IN",
        "AUTOSTARTING", "AUTOSTARTBLINK", "RTFWDISABLED", "INVERTERRESET", "INVERTERALARM",
        "INVERTEROVERLOAD", "LEFTSUPPINTERL", "RIGHTSUPPINTERL", "MACHINESTERTED"
    },
    "config>main>cmdio": {
        "STARTRESET", "STARTIN", "STOPIN", "MAINTRESET", "UNBALLEFT", "UNBALRIGHT", "TILTDISABLED"
    },
    "config>main>rsmio": {
        "MACHINESTARTED", "ALARMON", "ALARMSTOP", "MAINTON", "QUALITYEND", "QUALITYGOOD", "PARTEND", "PARTBEGIN"
    },
    "config>safety": {
        "EMGCYRESETBTN", "EMGCYPB", "HOLDTORUN", "HOLDTORUN2", "HOLDTORUNRC", "HOLDTORUNRC2", "HOLDTORUNERROR"
    },
    "config>pinchpreload": {
        "PINCHPRESS", "PRELOADUP", "PRELOADPINCHDISAB"
    },
    "config>rt": {"RTCOUPLED"},
    "config>grease": {
        "PUMPONCALC", "GREASEALARMCALC", "PUMPALARMCALC", "GREASETR", "GREASELEVEL"
    },
    "config>radiocontrol": {'RCV0', 'RCV1', 'RCV2', 'RCV3', 'RCV4', "RCLEFTSEL", "RCRIGHTSEL", "RCLEFTMEM",
                            "RCRIGHTMEM"},
    "config>bp": {"BPDISABLE1", "BPDISABLE2", "BPDISABLE3", "BPDISABLE4", "BPDISABLE5", "BPDISABLE6", "BPDISABLE7",
                  "BPDISABLE8", "BPDISABLE9", "BPDISABLE10", "BPDISABLE11", "BPDISABLE12"}
}

# Mappatura per indice del blocco "- in:" (etichette nominali)
IN_INDEX_LABELS = [
    "AUTOSEL", "TEACHSEL", "CYCLESEL", "STARTRESET", "REMOTESEL", "EMGCYPB", "CONSOLE2SEL", "CHROLLSEL", "x",
    "DEBALNOTPRESS", "CONSOLE1SEL", "SINGLEMOVSEL", "STARTIN", "STOPIN", "MACSTARTEDIN",
    "HOLDTORUN", "RTCOUPLED", "RCLEFTSEL", "PINCHPRESS", "RCRIGHTSEL",
    "STARTSENSORIN", "MAINTRESET", "MANSEL", "TESTSEL", "SEMIAUTOSEL", "HOLDTORUN2",
    "BPDISABLE1", "BPDISABLE2", "BPDISABLE3", "BPDISABLE4",
    "BPDISABLE5", "BPDISABLE6", "BPDISABLE7", "BPDISABLE8", "BPDISABLE9", "BPDISABLE10",
    "BPDISABLE11", "BPDISABLE12", "AUTOMODE", "AUTOCYCLEMODE", "AUTOSTEPMODE", "SEMIAUTOMODE",
    "TEACHMODE", "MANMODE", "CONSOLE1MODE", "CONSOLE2MODE", "REMOTEMODE", "CHROLLMODE", "SINGLEMOVMODE",
    "MACHINESTARTED", "x", "PUMPONCALC", "GREASEALARMCALC", "PUMPALARMCALC", "x", "x", "ALARMON", "x", "ALARMSTOP",
    "MAINTON", "RTFWDISABLED", "RCLEFTMEM", "x", "RCRIGHTMEM", "HOLDTORUNERROR", "x", "x", "x",
    "MICROSEL", "x", "QUALITYEND", "AUTOSTARTBLINK", "QUALITYGOOD", "PARTEND", "x", "PARTBEGIN",
    "x", "TILTDISABLED", "x", "x", "x", "x", "x", "x", "x", "x",
    "x", "x", "x", "x", "x", "RCV0", "RCV1", "RCV2", "RCV3", "RCV4",
    "x", "x", "x", "x", "x", "x", "x", "x", "x", "EMGCYRESETBTN",
    "x", "x", "INVERTERRESET", "INVERTERALARM", "AUTOSTARTING", "x", "x", "HOLDTORUNRC", "PRELOADUP",
    "PRELOADPINCHDISAB",
    "x", "x", "x", "x", "UNBALLEFT", "UNBALRIGHT", "INVERTEROVERLOAD", "LEFTSUPPINTERL", "GREASELEVEL", "GREASETR",
    "STARTSENSOR2IN", "HOLDTORUNRC2", "ROLLTILTBALANCED", "x", "x", "x", "RIGHTSUPPINTERL", "x", "x", "x"
]


def _label_from_in_index(idx: int) -> Optional[str]:
    if 0 <= idx < len(IN_INDEX_LABELS):
        lab = IN_INDEX_LABELS[idx]
        if isinstance(lab, str) and lab.strip().lower() != 'x' and lab.strip() != '':
            return lab.strip()
    return None


def _origin_from_in_index(idx: int) -> Optional[str]:
    lab = _label_from_in_index(idx)
    return _infer_in_origin(lab) if lab else None


def _normalize_label(s: str) -> str:
    # Uppercase e rimuove tutto ciò che non è A-Z/0-9 per confronti robusti
    return re.sub(r'[^A-Z0-9]', '', str(s).strip().upper())


def _infer_in_origin(label: str) -> Optional[str]:
    if not isinstance(label, str) or not label.strip():
        return None
    L = _normalize_label(label)

    # matching contro l'elenco noto, ma normalizzato
    for origin, names in _IN_ORIGIN_SETS.items():
        for n in names:
            if _normalize_label(n) == L:
                return origin
    return None


def _pair_in_arrays(in_arrays: List[List[Any]]) -> List[Tuple[int, Optional[List[Any]], Optional[List[Any]]]]:
    numeric = [(i, a) for i, a in enumerate(in_arrays) if _is_mostly_ints(a)]
    labels = [(i, a) for i, a in enumerate(in_arrays) if _is_mostly_strings(a)]

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


def search_in_field_matches(obj_node: Any, target_number: int) -> List[Tuple[int, int, Optional[str], Optional[str]]]:
    """
    Cerca il numero 'target_number' all'interno degli array '- in:' dovunque nel documento.
    Preferisce l'etichetta dalla lista labels abbinata; se mancante/insufficiente/'x',
    usa la mappatura per indice (IN_INDEX_LABELS) per ricavare label e origine.
    Ritorna: (pair_id, index, label_opzionale, origine_opzionale)
    """
    results: List[Tuple[int, int, Optional[str], Optional[str]]] = []
    in_arrays = _find_in_arrays(obj_node)
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
                label = _label_from_in_index(idx)

            # 3) calcola l'origine
            origin = _infer_in_origin(label) if label else _origin_from_in_index(idx)

            results.append((pid, idx, label, origin))

    return results


def _build_download_url(addr: str) -> str:
    """
    Costruisce l'URL finale a partire da un input tipo:
      - 10.3.73.177
      - http://10.3.73.177
      - https://10.3.73.177
      - https://10.3.73.177/UserFiles?Name=config.yaml&Action=DOWNLOAD
    Se l'input NON contiene '://', assume https://<addr> + path fisso richiesto.
    """
    addr = addr.strip()
    path = '/UserFiles?Name=config.yaml&Action=DOWNLOAD'
    if '://' in addr:
        # Se l'utente ha già messo il path completo, lo usiamo com'è.
        if '?' in addr or addr.endswith('/UserFiles') or '/UserFiles' in addr:
            return addr
        # Altrimenti aggiungiamo il path richiesto
        return addr.rstrip('/') + path
    # Default: https
    return f'https://{addr}{path}'


def download_file(url: str, dest_path: Path) -> None:
    """
    Scarica il file dall'URL fornito e lo salva in dest_path.
    Connessione NON protetta (verify=False). Se HTTPS fallisce, tenta HTTP.
    """
    print('Download in corso... (connessione non protetta / certificato non verificato)')
    try:
        _warnings.simplefilter('ignore', InsecureRequestWarning)  # sopprimi warning
    except Exception:
        pass

    try:
        r = requests.get(url, timeout=60, verify=False)
        r.raise_for_status()
        dest_path.write_bytes(r.content)
    except Exception as e_https:
        # Fallback a HTTP se l'URL era https://<host>/...
        try:
            if url.startswith('https://'):
                url_http = 'http://' + url[len('https://'):]
                r = requests.get(url_http, timeout=60)
                r.raise_for_status()
                dest_path.write_bytes(r.content)
            else:
                raise
        except Exception as e_http:
            raise RuntimeError(f'Errore nel download.\nHTTPS: {e_https}\nHTTP: {e_http}') from e_http

    print(f'File salvato in: {dest_path}')


def choose_and_prepare_config() -> Path:
    base_dir = get_run_dir()  # <- usa la cartella dell'eseguibile se frozen

    print("Selezione sorgente file 'config.yaml'")
    print("  [1] Usa file locale (stessa cartella dell'eseguibile)")
    print("  [2] Scarica da internet e salva accanto all'eseguibile (connessione NON protetta)")
    choice = input("Scelta: ").strip()

    try:
        choice = int(choice)
    except ValueError:
        print("Opzione non valida")
        sys.exit(1)

    if choice == 2:
        base = input("Inserisci indirizzo/IP (es: 10.3.73.177 oppure https://10.3.73.177): ").strip()
        if not base:
            print("Indirizzo non valido.")
            sys.exit(1)
        url = _build_download_url(base)
        dest = base_dir / "config.yaml"  # <<-- salva accanto all'eseguibile
        try:
            download_file(url, dest)
        except PermissionError:
            # fallback se la cartella dell'eseguibile non è scrivibile (es. Program Files)
            fallback = Path.home() / "Documents" / "search_config" / "config.yaml"
            fallback.parent.mkdir(parents=True, exist_ok=True)
            print(f"Permesso negato su {dest}. Salvo in {fallback}")
            download_file(url, fallback)
            return fallback
        except Exception as e:
            print(f"Errore nel download: {e}")
            sys.exit(1)
        return dest
    elif choice == 1:
        path = base_dir / "config.yaml"  # <<-- cerca accanto all'eseguibile
        if not path.exists():
            # opzionale: prova anche nella working dir se diverso
            wd_path = Path.cwd() / "config.yaml"
            if wd_path.exists():
                print(f"File non trovato in {path}, uso {wd_path}")
                return wd_path
            print(f"File locale non trovato: {path}")
            sys.exit(1)
        return path
    else:
        print("Opzione non valida")
        sys.exit(1)


def _pause_if_frozen():
    if getattr(sys, "frozen", False):  # eseguibile PyInstaller
        try:
            input("\nPremi Invio per chiudere...")
        except EOFError:
            pass


def main():
    # 1) Carico una volta il config
    cfg_path = choose_and_prepare_config()

    try:
        data = load_yaml(str(cfg_path))
    except Exception as e:
        print(f"Errore nel parsing YAML: {e}")
        _pause_if_frozen()
        return

    commessa = get_commessa_from_param(data)
    if commessa:
        print(f"Caricato config della commessa: {commessa}")

    # 2) Loop interattivo: ripeti la domanda dopo ogni ricerca
    while True:
        print("\n" + "-" * 60)
        tipo_raw = input("Che tipo stai cercando? (1=DI, 2=AI, 3=DO, 4=AO, 5=SYSTEM, Invio per uscire): ").strip().lower()
        if tipo_raw in ("", "q", "quit", "exit", "esci"):
            print("Uscita.")
            _pause_if_frozen()
            return

        try:
            tipo = int(tipo_raw)
        except ValueError:
            print("Tipo non valido. Inserisci 1, 2, 3, 4 o 5.")
            continue

        if tipo not in (1, 2, 3, 4, 5):
            print("Tipo non valido. Usa 1=DI, 2=AI, 3=DO, 4=AO, 5=SYSTEM.")
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
                        nm = row[0] if (isinstance(row, list) and row and isinstance(row[0], (str, int, float))) else None
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

        # Per DI/AI/DO/AO (1..4) chiedo il numero da cercare
        target_str = input("Inserisci il numero da cercare (Invio per tornare al menu): ").strip()
        if not target_str:
            continue
        try:
            target_number = int(target_str)
        except ValueError:
            print("Numero non valido.")
            continue

        print("-" * 60)

        if tipo == 1:
            run_di_search(data, target_number)
        elif tipo == 2:
            # ---- Ricerche su AI ----
            ao_list = (data.get('io') or {}).get('ao')
            if ao_list:
                matches = search_ai_in_ao_matches(ao_list, target_number, only_bus=True)
                if matches:
                    for ao_idx, where, name in matches:
                        if name:
                            print(f"{ao_idx} - {where} match - AO name: {name}")
                        else:
                            print(f"{ao_idx} - {where} match")
                else:
                    print("Nessuna referenza trovata negli AO (IN/AODUAL).")
            else:
                print("Sezione 'ao' non trovata.")

        elif tipo in (3, 4):
            print("Ricerca per DO/AO (DI target) non ancora implementata qui.")


def print_in_columns(entries: List[str], cols: int = 3) -> None:
    if not entries:
        return
    colw = max(len(s) for s in entries) + 2  # padding
    for i in range(0, len(entries), cols):
        row = entries[i:i+cols]
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
