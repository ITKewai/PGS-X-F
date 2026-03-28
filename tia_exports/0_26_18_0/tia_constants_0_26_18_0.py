# Auto-generato da main_import.py
__version__ = '0.26.18.0'

# --- DB DATA_CONFIG.db ---
class DATA_CONFIG:
    def __init__(self):
        self._defaults = {}
        self.PLCVersion = None  # String["DIM_STRINGNAME"] // scritto su Settings
        self._defaults['PLCVersion'] = None
        self.PLCVersion1 = -1  # Int
        self._defaults['PLCVersion1'] = -1
        self.PLCVersion2 = -1  # Int
        self._defaults['PLCVersion2'] = -1
        self.PLCVersion3 = -1  # Int
        self._defaults['PLCVersion3'] = -1
        self.PLCVersion4 = -1  # Int
        self._defaults['PLCVersion4'] = -1
        self.CFGVersion = -1  # Int // PLCVersion1 * 100 + PLCVersion2
        self._defaults['CFGVersion'] = -1
        self.SerType = -1  # Int // tipo dati Deserialize
        self._defaults['SerType'] = -1
        self.SerCurrInd = -1  # Int // indice blocco corrente Deserialize
        self._defaults['SerCurrInd'] = -1
        self.SerCurrLast = -1  # Int // indice ultimo blocco Deserialize
        self._defaults['SerCurrLast'] = -1
        self.SerIndStat = -1  # Int
        self._defaults['SerIndStat'] = -1
        self.SerTotRot = 0.0  # Real
        self._defaults['SerTotRot'] = 0.0
        self.InstallTime = None  # DTL // Impostato su comando da HMI
        self._defaults['InstallTime'] = None
        self.ConfigSaveReqTime = None  # Time
        self._defaults['ConfigSaveReqTime'] = None
        self.ConfigSaveReqTimeout = -1  # ULInt
        self._defaults['ConfigSaveReqTimeout'] = -1
        self.ConfigSaveReqStart = False  # Bool
        self._defaults['ConfigSaveReqStart'] = False
        self.TabstatReqTime = None  # Time
        self._defaults['TabstatReqTime'] = None
        self.TabstatReqTimeout = -1  # ULInt
        self._defaults['TabstatReqTimeout'] = -1
        self.ProgReqHMITime = None  # Time
        self._defaults['ProgReqHMITime'] = None
        self.ProgReqHMITimeout = -1  # ULInt
        self._defaults['ProgReqHMITimeout'] = -1
        self.SaveConfigReq = False  # Bool
        self._defaults['SaveConfigReq'] = False
        self.SaveConfigCurrStep = -1  # Int
        self._defaults['SaveConfigCurrStep'] = -1
        self.DeletingFile = False  # Bool
        self._defaults['DeletingFile'] = False
        self.SavingFile = False  # Bool // Scrittura file su WebServer in corso
        self._defaults['SavingFile'] = False
        self.DebugInd = -1  # Int
        self._defaults['DebugInd'] = -1
        self.DebugInd2 = -1  # Int
        self._defaults['DebugInd2'] = -1
        self.Config_Header = [-1] * (MAX_HEADER + 1)  # Array[0.."MAX_HEADER"] of Int // SN,FileType,FileTypeVersion,FileVersion
        self._defaults['Config_Header'] = [-1] * (MAX_HEADER + 1)
        self.AxisFunInd = [-1] * (MAX_ASSEFUNIND + 1)  # Array[0.."MAX_ASSEFUNIND"] of Int
        self._defaults['AxisFunInd'] = [-1] * (MAX_ASSEFUNIND + 1)
        self.InInd = [-1] * (MAX_STATOBOOL + 1)  # Array[0.."MAX_STATOBOOL"] of Int
        self._defaults['InInd'] = [-1] * (MAX_STATOBOOL + 1)
        self.OutInd = [-1] * (MAX_STATOBOOL + 1)  # Array[0.."MAX_STATOBOOL"] of Int
        self._defaults['OutInd'] = [-1] * (MAX_STATOBOOL + 1)
        self.ParamString = [None] * (MAX_PARAMSTRING + 1)  # Array[0.."MAX_PARAMSTRING"] of String["DIM_STRINGNAME"]
        self._defaults['ParamString'] = [None] * (MAX_PARAMSTRING + 1)
        self.ParamBool = [False] * (MAX_PARAMBOOL + 1)  # Array[0.."MAX_PARAMBOOL"] of Bool
        self._defaults['ParamBool'] = [False] * (MAX_PARAMBOOL + 1)
        self.ParamInt = [-1] * (MAX_PARAMINT + 1)  # Array[0.."MAX_PARAMINT"] of Int
        self._defaults['ParamInt'] = [-1] * (MAX_PARAMINT + 1)
        self.ParamRealCfg = [0.0] * (MAX_PARAMREAL + 1)  # Array[0.."MAX_PARAMREAL"] of Real
        self._defaults['ParamRealCfg'] = [0.0] * (MAX_PARAMREAL + 1)
        self.ParamReal = [0.0] * (MAX_PARAMREAL + 1)  # Array[0.."MAX_PARAMREAL"] of Real
        self._defaults['ParamReal'] = [0.0] * (MAX_PARAMREAL + 1)
        self.ParamRealType = [-1] * (MAX_PARAMREAL + 1)  # Array[0.."MAX_PARAMREAL"] of Int
        self._defaults['ParamRealType'] = [-1] * (MAX_PARAMREAL + 1)
        self.ParamRealFC = [0.0] * (MAX_PARAMREAL + 1)  # Array[0.."MAX_PARAMREAL"] of Real
        self._defaults['ParamRealFC'] = [0.0] * (MAX_PARAMREAL + 1)
        self.ParamRealOffset = [0.0] * (MAX_PARAMREAL + 1)  # Array[0.."MAX_PARAMREAL"] of Real
        self._defaults['ParamRealOffset'] = [0.0] * (MAX_PARAMREAL + 1)
        self.IO_Name = [None] * (MAX_IO + 1)  # Array[0.."MAX_IO"] of String["DIM_STRINGNAME"]
        self._defaults['IO_Name'] = [None] * (MAX_IO + 1)
        self.IO_Param = [Type_IOParam() for _ in range(MAX_IO + 1)]  # Array[0.."MAX_IO"] of "Type_IOParam"
        self._defaults['IO_Param'] = [Type_IOParam() for _ in range(MAX_IO + 1)]
        self.Axis_Name = [None] * (MAX_ASSE + 1)  # Array[0.."MAX_ASSE"] of String["DIM_STRINGID"]
        self._defaults['Axis_Name'] = [None] * (MAX_ASSE + 1)
        self.Axis_Param = [Type_AxisParam() for _ in range(MAX_ASSE + 1)]  # Array[0.."MAX_ASSE"] of "Type_AxisParam"
        self._defaults['Axis_Param'] = [Type_AxisParam() for _ in range(MAX_ASSE + 1)]
        self.Axis = [Type_Axis() for _ in range(MAX_ASSE + 1)]  # Array[0.."MAX_ASSE"] of "Type_Axis"
        self._defaults['Axis'] = [Type_Axis() for _ in range(MAX_ASSE + 1)]
        self.Input = [Type_Input() for _ in range(MAX_INPUT + 1)]  # Array[0.."MAX_INPUT"] of "Type_Input"
        self._defaults['Input'] = [Type_Input() for _ in range(MAX_INPUT + 1)]
        self.Input_Param = [Type_InputParam() for _ in range(MAX_INPUT + 1)]  # Array[0.."MAX_INPUT"] of "Type_InputParam"
        self._defaults['Input_Param'] = [Type_InputParam() for _ in range(MAX_INPUT + 1)]
        self.Feedback = [Type_Feedback() for _ in range(MAX_FEEDBACK + 1)]  # Array[0.."MAX_FEEDBACK"] of "Type_Feedback"
        self._defaults['Feedback'] = [Type_Feedback() for _ in range(MAX_FEEDBACK + 1)]
        self.Feedback_Param = [Type_FeedbackParam() for _ in range(MAX_FEEDBACK + 1)]  # Array[0.."MAX_FEEDBACK"] of "Type_FeedbackParam"
        self._defaults['Feedback_Param'] = [Type_FeedbackParam() for _ in range(MAX_FEEDBACK + 1)]
        self.PID = [Type_PID() for _ in range(MAX_PID + 1)]  # Array[0.."MAX_PID"] of "Type_PID"
        self._defaults['PID'] = [Type_PID() for _ in range(MAX_PID + 1)]
        self.PID_Param = [Type_PIDParam() for _ in range(MAX_PID + 1)]  # Array[0.."MAX_PID"] of "Type_PIDParam"
        self._defaults['PID_Param'] = [Type_PIDParam() for _ in range(MAX_PID + 1)]
        self.Output = [Type_Output() for _ in range(MAX_OUTPUT + 1)]  # Array[0.."MAX_OUTPUT"] of "Type_Output"
        self._defaults['Output'] = [Type_Output() for _ in range(MAX_OUTPUT + 1)]
        self.Output_Param = [Type_OutputParam() for _ in range(MAX_OUTPUT + 1)]  # Array[0.."MAX_OUTPUT"] of "Type_OutputParam"
        self._defaults['Output_Param'] = [Type_OutputParam() for _ in range(MAX_OUTPUT + 1)]
        self.Motor = [Type_Motor() for _ in range(MAX_MOTORE + 1)]  # Array[0.."MAX_MOTORE"] of "Type_Motor"
        self._defaults['Motor'] = [Type_Motor() for _ in range(MAX_MOTORE + 1)]
        self.Motor_Config = [False] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Bool
        self._defaults['Motor_Config'] = [False] * (MAX_MOTORE + 1)
        self.Motor_Selectable = [False] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Bool
        self._defaults['Motor_Selectable'] = [False] * (MAX_MOTORE + 1)
        self.Motor_LSInd = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_LSInd'] = [-1] * (MAX_MOTORE + 1)
        self.Motor_LS2Ind = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_LS2Ind'] = [-1] * (MAX_MOTORE + 1)
        self.Motor_CmdInd = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_CmdInd'] = [-1] * (MAX_MOTORE + 1)
        self.Motor_Cmd1Ind = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_Cmd1Ind'] = [-1] * (MAX_MOTORE + 1)
        self.Motor_Cmd2Ind = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_Cmd2Ind'] = [-1] * (MAX_MOTORE + 1)
        self.Motor_Cmd3Ind = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_Cmd3Ind'] = [-1] * (MAX_MOTORE + 1)
        self.Motor_StatInd = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_StatInd'] = [-1] * (MAX_MOTORE + 1)
        self.Motor_TRInd = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_TRInd'] = [-1] * (MAX_MOTORE + 1)
        self.Motor_TR2Ind = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_TR2Ind'] = [-1] * (MAX_MOTORE + 1)
        self.Motor_StartingInd = [-1] * (MAX_MOTORE + 1)  # Array[0.."MAX_MOTORE"] of Int
        self._defaults['Motor_StartingInd'] = [-1] * (MAX_MOTORE + 1)
        self.Alarm_Name = [None] * (MAX_ALARM + 1)  # Array[0.."MAX_ALARM"] of String["DIM_STRINGNAME"]
        self._defaults['Alarm_Name'] = [None] * (MAX_ALARM + 1)
        self.Alarm_Param = [Type_AlarmParam() for _ in range(MAX_ALARM + 1)]  # Array[0.."MAX_ALARM"] of "Type_AlarmParam"
        self._defaults['Alarm_Param'] = [Type_AlarmParam() for _ in range(MAX_ALARM + 1)]
        self.Stop_Num = -1  # Int
        self._defaults['Stop_Num'] = -1
        self.Stop_Name = [None] * (MAX_STOP + 1)  # Array[0.."MAX_STOP"] of String["DIM_STRINGNAME"]
        self._defaults['Stop_Name'] = [None] * (MAX_STOP + 1)
        self.Stop_Ind = [-1] * (MAX_STOP + 1)  # Array[0.."MAX_STOP"] of Int
        self._defaults['Stop_Ind'] = [-1] * (MAX_STOP + 1)
        self.Maint_Name = [None] * (MAX_MAINT + 1)  # Array[0.."MAX_MAINT"] of String["DIM_STRINGNAME"]
        self._defaults['Maint_Name'] = [None] * (MAX_MAINT + 1)
        self.Maint_Param = [Type_MaintParam() for _ in range(MAX_MAINT + 1)]  # Array[0.."MAX_MAINT"] of "Type_MaintParam"
        self._defaults['Maint_Param'] = [Type_MaintParam() for _ in range(MAX_MAINT + 1)]
        self.Toolset_Name = [None] * (MAX_TOOLSET + 1)  # Array[0.."MAX_TOOLSET"] of String["DIM_STRINGNAME"]
        self._defaults['Toolset_Name'] = [None] * (MAX_TOOLSET + 1)
        self.Toolset_Param = [Type_ToolsetParam() for _ in range(MAX_TOOLSET + 1)]  # Array[0.."MAX_TOOLSET"] of "Type_ToolsetParam"
        self._defaults['Toolset_Param'] = [Type_ToolsetParam() for _ in range(MAX_TOOLSET + 1)]
        self.UM_FC = [0.0] * (MAX_UM + 1)  # Array[0.."MAX_UM"] of Real
        self._defaults['UM_FC'] = [0.0] * (MAX_UM + 1)
        self.UM_FC_Met = [0.0] * (MAX_UM + 1)  # Array[0.."MAX_UM"] of Real
        self._defaults['UM_FC_Met'] = [0.0] * (MAX_UM + 1)
        self.UM_FC_Imp = [0.0] * (MAX_UM + 1)  # Array[0.."MAX_UM"] of Real
        self._defaults['UM_FC_Imp'] = [0.0] * (MAX_UM + 1)


class Type_StatParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        seqid (Int := -1):
        statpos (Int := -1):
        pos (Int := -1):
        objtype (Int := -1):
        ival (Int):
        rval (Real):
        addr (Int := -1):
        next (Int := -1):
    """
    def __init__(self):
        self._defaults = {}
        self.seqid = -1  # Int := -1
        self._defaults['seqid'] = -1
        self.statpos = -1  # Int := -1
        self._defaults['statpos'] = -1
        self.pos = -1  # Int := -1
        self._defaults['pos'] = -1
        self.objtype = -1  # Int := -1
        self._defaults['objtype'] = -1
        self.ival = -1  # Int
        self._defaults['ival'] = -1
        self.rval = 0.0  # Real
        self._defaults['rval'] = 0.0
        self.addr = -1  # Int := -1
        self._defaults['addr'] = -1
        self.next = -1  # Int := -1
        self._defaults['next'] = -1

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_StatParam {fields}>"



class Type_Stat:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        seqid (Int := -1):
        pos (Int := -1):
        cod (Int := -1):
        firstparam (Int := -1):
        lastparam (Int := -1):
        next (Int := -1):
        disabled (Bool):
        prim (Int):
    """
    def __init__(self):
        self._defaults = {}
        self.seqid = -1  # Int := -1
        self._defaults['seqid'] = -1
        self.pos = -1  # Int := -1
        self._defaults['pos'] = -1
        self.cod = -1  # Int := -1
        self._defaults['cod'] = -1
        self.firstparam = -1  # Int := -1
        self._defaults['firstparam'] = -1
        self.lastparam = -1  # Int := -1
        self._defaults['lastparam'] = -1
        self.next = -1  # Int := -1
        self._defaults['next'] = -1
        self.disabled = False  # Bool
        self._defaults['disabled'] = False
        self.prim = -1  # Int
        self._defaults['prim'] = -1

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_Stat {fields}>"



class Type_ToolsetOutputParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        intval (Array[0.."MAX_TOOLSETOUTPUTINT"] of Int := [2(-1)]):
        dintval (Array[0.."MAX_TOOLSETOUTPUTDINT"] of DInt):
    """
    def __init__(self):
        self._defaults = {}
        self.intval = [-1] * (MAX_TOOLSETOUTPUTINT + 1)  # Array[0.."MAX_TOOLSETOUTPUTINT"] of Int := [2(-1)]
        self._defaults['intval'] = [-1] * (MAX_TOOLSETOUTPUTINT + 1)
        self.dintval = [-1] * (MAX_TOOLSETOUTPUTDINT + 1)  # Array[0.."MAX_TOOLSETOUTPUTDINT"] of DInt
        self._defaults['dintval'] = [-1] * (MAX_TOOLSETOUTPUTDINT + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_ToolsetOutputParam {fields}>"



class Type_AlarmParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        boolval (Array[0.."MAX_ALARMBOOL"] of Bool):
        intval (Array[0.."MAX_ALARMINT"] of Int := [10(-1)]):
    """
    def __init__(self):
        self._defaults = {}
        self.boolval = [False] * (MAX_ALARMBOOL + 1)  # Array[0.."MAX_ALARMBOOL"] of Bool
        self._defaults['boolval'] = [False] * (MAX_ALARMBOOL + 1)
        self.intval = [-1] * (MAX_ALARMINT + 1)  # Array[0.."MAX_ALARMINT"] of Int := [10(-1)]
        self._defaults['intval'] = [-1] * (MAX_ALARMINT + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_AlarmParam {fields}>"



class Type_Teach:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        teach_stat (Array[0.."MAX_TEACHSTAT"] of Bool):
    """
    def __init__(self):
        self._defaults = {}
        self.teach_stat = [False] * (MAX_TEACHSTAT + 1)  # Array[0.."MAX_TEACHSTAT"] of Bool
        self._defaults['teach_stat'] = [False] * (MAX_TEACHSTAT + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_Teach {fields}>"



class Type_Seq:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        SeqNum (Int):
        SeqFirst (Int := -1):
        SeqLast (Int := -1):
        SeqCurrInd (Int := -1):
        SeqId (Array[0.."MAX_SEQ"] of Int):
        SeqTyp (Array[0.."MAX_SEQ"] of Int):
        SeqFirstStat (Array[0.."MAX_SEQ"] of Int):
        SeqLastStat (Array[0.."MAX_SEQ"] of Int):
        SeqNext (Array[0.."MAX_SEQ"] of Int):
        SeqNumStat (Array[0.."MAX_SEQ"] of Int):
        StatNum (Int):
        Stat (Array[0.."MAX_STAT"] of "Type_Stat"):
        StatParamNum (Int):
        StatParam (Array[0.."MAX_STATPARAM"] of "Type_StatParam"):
        SeqStartCurrId (Int := -1):
        SeqStartPrevId (Int := -1):
        StatCurrInd (Int := -1):
        SeqMode (Bool):
        SeqModePrev (Bool):
        SeqTerm (Bool):
        StatTerm (Bool):
        StatNew (Bool):
        StackLevel (Int):
        StackLevelAuto (Int):
        StackRet (Array[0.."MAX_SEQSTACK"] of Int):
        DelayElapsedTime (Int):
        CurrProgSeq (Int):
        PrevProgSeq (Int):
        StatRunning (Int):
        StatNumAxesStarted (Int):
        CurrStatCod (Int):
        PrevStatCod (Int):
        StatStartInd (Int := -1):
    """
    def __init__(self):
        self._defaults = {}
        self.SeqNum = -1  # Int
        self._defaults['SeqNum'] = -1
        self.SeqFirst = -1  # Int := -1
        self._defaults['SeqFirst'] = -1
        self.SeqLast = -1  # Int := -1
        self._defaults['SeqLast'] = -1
        self.SeqCurrInd = -1  # Int := -1
        self._defaults['SeqCurrInd'] = -1
        self.SeqId = [-1] * (MAX_SEQ + 1)  # Array[0.."MAX_SEQ"] of Int
        self._defaults['SeqId'] = [-1] * (MAX_SEQ + 1)
        self.SeqTyp = [-1] * (MAX_SEQ + 1)  # Array[0.."MAX_SEQ"] of Int
        self._defaults['SeqTyp'] = [-1] * (MAX_SEQ + 1)
        self.SeqFirstStat = [-1] * (MAX_SEQ + 1)  # Array[0.."MAX_SEQ"] of Int
        self._defaults['SeqFirstStat'] = [-1] * (MAX_SEQ + 1)
        self.SeqLastStat = [-1] * (MAX_SEQ + 1)  # Array[0.."MAX_SEQ"] of Int
        self._defaults['SeqLastStat'] = [-1] * (MAX_SEQ + 1)
        self.SeqNext = [-1] * (MAX_SEQ + 1)  # Array[0.."MAX_SEQ"] of Int
        self._defaults['SeqNext'] = [-1] * (MAX_SEQ + 1)
        self.SeqNumStat = [-1] * (MAX_SEQ + 1)  # Array[0.."MAX_SEQ"] of Int
        self._defaults['SeqNumStat'] = [-1] * (MAX_SEQ + 1)
        self.StatNum = -1  # Int
        self._defaults['StatNum'] = -1
        self.Stat = None  # Array[0.."MAX_STAT"] of "Type_Stat"
        self._defaults['Stat'] = None
        self.StatParamNum = -1  # Int
        self._defaults['StatParamNum'] = -1
        self.StatParam = None  # Array[0.."MAX_STATPARAM"] of "Type_StatParam"
        self._defaults['StatParam'] = None
        self.SeqStartCurrId = -1  # Int := -1
        self._defaults['SeqStartCurrId'] = -1
        self.SeqStartPrevId = -1  # Int := -1
        self._defaults['SeqStartPrevId'] = -1
        self.StatCurrInd = -1  # Int := -1
        self._defaults['StatCurrInd'] = -1
        self.SeqMode = False  # Bool
        self._defaults['SeqMode'] = False
        self.SeqModePrev = False  # Bool
        self._defaults['SeqModePrev'] = False
        self.SeqTerm = False  # Bool
        self._defaults['SeqTerm'] = False
        self.StatTerm = False  # Bool
        self._defaults['StatTerm'] = False
        self.StatNew = False  # Bool
        self._defaults['StatNew'] = False
        self.StackLevel = -1  # Int
        self._defaults['StackLevel'] = -1
        self.StackLevelAuto = -1  # Int
        self._defaults['StackLevelAuto'] = -1
        self.StackRet = [-1] * (MAX_SEQSTACK + 1)  # Array[0.."MAX_SEQSTACK"] of Int
        self._defaults['StackRet'] = [-1] * (MAX_SEQSTACK + 1)
        self.DelayElapsedTime = -1  # Int
        self._defaults['DelayElapsedTime'] = -1
        self.CurrProgSeq = -1  # Int
        self._defaults['CurrProgSeq'] = -1
        self.PrevProgSeq = -1  # Int
        self._defaults['PrevProgSeq'] = -1
        self.StatRunning = -1  # Int
        self._defaults['StatRunning'] = -1
        self.StatNumAxesStarted = -1  # Int
        self._defaults['StatNumAxesStarted'] = -1
        self.CurrStatCod = -1  # Int
        self._defaults['CurrStatCod'] = -1
        self.PrevStatCod = -1  # Int
        self._defaults['PrevStatCod'] = -1
        self.StatStartInd = -1  # Int := -1
        self._defaults['StatStartInd'] = -1

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_Seq {fields}>"



class Type_PIDParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        realval (Array[0.."MAX_PIDREAL"] of Real):
    """
    def __init__(self):
        self._defaults = {}
        self.realval = [0.0] * (MAX_PIDREAL + 1)  # Array[0.."MAX_PIDREAL"] of Real
        self._defaults['realval'] = [0.0] * (MAX_PIDREAL + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_PIDParam {fields}>"



class Type_PID:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        sp (Real):
        in_ (Real):
        reset (Bool):
        out1 (Real):
        out2 (Real):
    """
    def __init__(self):
        self._defaults = {}
        self.sp = 0.0  # Real
        self._defaults['sp'] = 0.0
        self.in_ = 0.0  # Real
        self._defaults['in_'] = 0.0
        self.reset = False  # Bool
        self._defaults['reset'] = False
        self.out1 = 0.0  # Real
        self._defaults['out1'] = 0.0
        self.out2 = 0.0  # Real
        self._defaults['out2'] = 0.0

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_PID {fields}>"



class Type_OutputParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        intval (Array[0.."MAX_OUTPUTINT"] of Int := [14(-1)]):
        dintval (Array[0.."MAX_OUTPUTDINT"] of DInt):
        realval (Array[0.."MAX_OUTPUTREAL"] of Real := [0.0, 100.0, 0.0, 100.0, 2(0.0), 2(20.0), 2(40.0), 2(60.0), 2(80.0), 2(100.0), 2(0.0), 2(20.0), 2(40.0), 2(60.0), 2(80.0), 2(100.0)]):
    """
    def __init__(self):
        self._defaults = {}
        self.intval = [-1] * (MAX_OUTPUTINT + 1)  # Array[0.."MAX_OUTPUTINT"] of Int := [14(-1)]
        self._defaults['intval'] = [-1] * (MAX_OUTPUTINT + 1)
        self.dintval = [-1] * (MAX_OUTPUTDINT + 1)  # Array[0.."MAX_OUTPUTDINT"] of DInt
        self._defaults['dintval'] = [-1] * (MAX_OUTPUTDINT + 1)
        self.realval = [0.0] * (MAX_OUTPUTREAL + 1)  # Array[0.."MAX_OUTPUTREAL"] of Real := [0.0, 100.0, 0.0, 100.0, 2(0.0), 2(20.0), 2(40.0), 2(60.0), 2(80.0), 2(100.0), 2(0.0), 2(20.0), 2(40.0), 2(60.0), 2(80.0), 2(100.0)]
        self._defaults['realval'] = [0.0] * (MAX_OUTPUTREAL + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_OutputParam {fields}>"



class Type_Output:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        val_in (Real):
        val_norm (Real):
        val_scaled (Real):
        out_dig1 (Bool):
        out_dig2 (Bool):
        out_analog1 (DInt):
        out_analog2 (DInt):
        flagao (Bool):
        indasse (Int := -1):
        enab (Bool):
        preset (Bool):
        preval (Real):
        preind2 (Int):
        indpslcan (Int := -1):
    """
    def __init__(self):
        self._defaults = {}
        self.val_in = 0.0  # Real
        self._defaults['val_in'] = 0.0
        self.val_norm = 0.0  # Real
        self._defaults['val_norm'] = 0.0
        self.val_scaled = 0.0  # Real
        self._defaults['val_scaled'] = 0.0
        self.out_dig1 = False  # Bool
        self._defaults['out_dig1'] = False
        self.out_dig2 = False  # Bool
        self._defaults['out_dig2'] = False
        self.out_analog1 = -1  # DInt
        self._defaults['out_analog1'] = -1
        self.out_analog2 = -1  # DInt
        self._defaults['out_analog2'] = -1
        self.flagao = False  # Bool
        self._defaults['flagao'] = False
        self.indasse = -1  # Int := -1
        self._defaults['indasse'] = -1
        self.enab = False  # Bool
        self._defaults['enab'] = False
        self.preset = False  # Bool
        self._defaults['preset'] = False
        self.preval = 0.0  # Real
        self._defaults['preval'] = 0.0
        self.preind2 = -1  # Int
        self._defaults['preind2'] = -1
        self.indpslcan = -1  # Int := -1
        self._defaults['indpslcan'] = -1

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_Output {fields}>"



class Type_Motor:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        timeout (Int):
        seq (Bool):
        opt (Bool):
        default (Bool):
        timeout2 (Int):
        typ (Int): tipo motore per nome e icona HMI
        diff (ULInt):
        diff2 (ULInt):
        seqok (Bool):
        timeoutbtn (Int):
        timeout3 (Int):
        timeout4 (Int):
    """
    def __init__(self):
        self._defaults = {}
        self.timeout = -1  # Int
        self._defaults['timeout'] = -1
        self.seq = False  # Bool
        self._defaults['seq'] = False
        self.opt = False  # Bool
        self._defaults['opt'] = False
        self.default = False  # Bool
        self._defaults['default'] = False
        self.timeout2 = -1  # Int
        self._defaults['timeout2'] = -1
        self.typ = -1  # Int // tipo motore per nome e icona HMI
        self._defaults['typ'] = -1
        self.diff = -1  # ULInt
        self._defaults['diff'] = -1
        self.diff2 = -1  # ULInt
        self._defaults['diff2'] = -1
        self.seqok = False  # Bool
        self._defaults['seqok'] = False
        self.timeoutbtn = -1  # Int
        self._defaults['timeoutbtn'] = -1
        self.timeout3 = -1  # Int
        self._defaults['timeout3'] = -1
        self.timeout4 = -1  # Int
        self._defaults['timeout4'] = -1

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_Motor {fields}>"



class Type_MaintParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        boolval (Array[0.."MAX_MAINTBOOL"] of Bool):
        intval (Array[0.."MAX_MAINTINT"] of Int):
    """
    def __init__(self):
        self._defaults = {}
        self.boolval = [False] * (MAX_MAINTBOOL + 1)  # Array[0.."MAX_MAINTBOOL"] of Bool
        self._defaults['boolval'] = [False] * (MAX_MAINTBOOL + 1)
        self.intval = [-1] * (MAX_MAINTINT + 1)  # Array[0.."MAX_MAINTINT"] of Int
        self._defaults['intval'] = [-1] * (MAX_MAINTINT + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_MaintParam {fields}>"



class Type_IORef:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        FlagTot (Bool):
        FlagTime (Bool):
        Int (= [12(-1)]):
    """
    def __init__(self):
        self._defaults = {}
        self.FlagTot = False  # Bool
        self._defaults['FlagTot'] = False
        self.FlagTime = False  # Bool
        self._defaults['FlagTime'] = False
        self.Int = None  # = [12(-1)]
        self._defaults['Int'] = None

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_IORef {fields}>"



class Type_IO:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        Ind (Int := -1):
        Stato (Int):
        BVal (Bool):
        IVal (Int):
        DVal (DInt):
        RVal (Real):
        Offset (Real):
        BProgVal (Bool):
        DProgVal (DInt):
    """
    def __init__(self):
        self._defaults = {}
        self.Ind = -1  # Int := -1
        self._defaults['Ind'] = -1
        self.Stato = -1  # Int
        self._defaults['Stato'] = -1
        self.BVal = False  # Bool
        self._defaults['BVal'] = False
        self.IVal = -1  # Int
        self._defaults['IVal'] = -1
        self.DVal = -1  # DInt
        self._defaults['DVal'] = -1
        self.RVal = 0.0  # Real
        self._defaults['RVal'] = 0.0
        self.Offset = 0.0  # Real
        self._defaults['Offset'] = 0.0
        self.BProgVal = False  # Bool
        self._defaults['BProgVal'] = False
        self.DProgVal = -1  # DInt
        self._defaults['DProgVal'] = -1

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_IO {fields}>"



class Type_InputParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        boolval (Array[0.."MAX_INPUTBOOL"] of Bool):
        intval (Array[0.."MAX_INPUTINT"] of Int := [5(-1), 0, 2(-1), 0, 6(-1)]):
        dintvalcfg (Array[0.."MAX_INPUTDINT"] of DInt):
        dintval (Array[0.."MAX_INPUTDINT"] of DInt := [0, 100, 0, 100]):
    """
    def __init__(self):
        self._defaults = {}
        self.boolval = [False] * (MAX_INPUTBOOL + 1)  # Array[0.."MAX_INPUTBOOL"] of Bool
        self._defaults['boolval'] = [False] * (MAX_INPUTBOOL + 1)
        self.intval = [-1] * (MAX_INPUTINT + 1)  # Array[0.."MAX_INPUTINT"] of Int := [5(-1), 0, 2(-1), 0, 6(-1)]
        self._defaults['intval'] = [-1] * (MAX_INPUTINT + 1)
        self.dintvalcfg = [-1] * (MAX_INPUTDINT + 1)  # Array[0.."MAX_INPUTDINT"] of DInt
        self._defaults['dintvalcfg'] = [-1] * (MAX_INPUTDINT + 1)
        self.dintval = [-1] * (MAX_INPUTDINT + 1)  # Array[0.."MAX_INPUTDINT"] of DInt := [0, 100, 0, 100]
        self._defaults['dintval'] = [-1] * (MAX_INPUTDINT + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_InputParam {fields}>"



class Type_Input:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        val (Real):
        val_prev (Real):
        indasse (Int := -1):
        enab (Bool := true):
    """
    def __init__(self):
        self._defaults = {}
        self.val = 0.0  # Real
        self._defaults['val'] = 0.0
        self.val_prev = 0.0  # Real
        self._defaults['val_prev'] = 0.0
        self.indasse = -1  # Int := -1
        self._defaults['indasse'] = -1
        self.enab = False  # Bool := true
        self._defaults['enab'] = False

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_Input {fields}>"



class Type_IFMExcParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        intval (Array[0.."MAX_IFMEXCINT"] of Int := [4(-1)]):
    """
    def __init__(self):
        self._defaults = {}
        self.intval = [-1] * (MAX_IFMEXCINT + 1)  # Array[0.."MAX_IFMEXCINT"] of Int := [4(-1)]
        self._defaults['intval'] = [-1] * (MAX_IFMEXCINT + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_IFMExcParam {fields}>"



class Type_FeedbackParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        intval (Array[0.."MAX_FEEDBACKINT"] of Int := [5(-1)]):
        dintval (Array[0.."MAX_FEEDBACKDINT"] of DInt := [48, 32000]):
        realvalcfg (Array[0.."MAX_FEEDBACKREAL"] of Real):
        realval (Array[0.."MAX_FEEDBACKREAL"] of Real):
    """
    def __init__(self):
        self._defaults = {}
        self.intval = [-1] * (MAX_FEEDBACKINT + 1)  # Array[0.."MAX_FEEDBACKINT"] of Int := [5(-1)]
        self._defaults['intval'] = [-1] * (MAX_FEEDBACKINT + 1)
        self.dintval = [-1] * (MAX_FEEDBACKDINT + 1)  # Array[0.."MAX_FEEDBACKDINT"] of DInt := [48, 32000]
        self._defaults['dintval'] = [-1] * (MAX_FEEDBACKDINT + 1)
        self.realvalcfg = [0.0] * (MAX_FEEDBACKREAL + 1)  # Array[0.."MAX_FEEDBACKREAL"] of Real
        self._defaults['realvalcfg'] = [0.0] * (MAX_FEEDBACKREAL + 1)
        self.realval = [0.0] * (MAX_FEEDBACKREAL + 1)  # Array[0.."MAX_FEEDBACKREAL"] of Real
        self._defaults['realval'] = [0.0] * (MAX_FEEDBACKREAL + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_FeedbackParam {fields}>"



class Type_Feedback:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        val_in (DInt):
        val_scaled (Real):
        error (Int):
        val_scaled_prev (Real):
        setval (Bool):
        newval (Real):
        indasse (Int := -1):
        resetval (Bool):
    """
    def __init__(self):
        self._defaults = {}
        self.val_in = -1  # DInt
        self._defaults['val_in'] = -1
        self.val_scaled = 0.0  # Real
        self._defaults['val_scaled'] = 0.0
        self.error = -1  # Int
        self._defaults['error'] = -1
        self.val_scaled_prev = 0.0  # Real
        self._defaults['val_scaled_prev'] = 0.0
        self.setval = False  # Bool
        self._defaults['setval'] = False
        self.newval = 0.0  # Real
        self._defaults['newval'] = 0.0
        self.indasse = -1  # Int := -1
        self._defaults['indasse'] = -1
        self.resetval = False  # Bool
        self._defaults['resetval'] = False

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_Feedback {fields}>"



class Type_CANNodeParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        intval (Array[0.."MAX_CANNODEINT"] of Int := [3(-1)]):
    """
    def __init__(self):
        self._defaults = {}
        self.intval = [-1] * (MAX_CANNODEINT + 1)  # Array[0.."MAX_CANNODEINT"] of Int := [3(-1)]
        self._defaults['intval'] = [-1] * (MAX_CANNODEINT + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_CANNodeParam {fields}>"



class Type_AxisParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        boolval (Array[0.."MAX_ASSEBOOL"] of Bool):
        intval (Array[0.."MAX_ASSEINT"] of Int := [8(-1), 1, 18(-1), 100, 2(0), 15(-1), 2(0), 2000, 6(-1), 2(0), 100, 7(-1), 2(0), 2(-1), 0, 2, 25(-1)]):
        realvalcfg (Array[0.."MAX_ASSEREAL"] of Real):
        realval (Array[0.."MAX_ASSEREAL"] of Real):
        fcval (Array[0.."MAX_ASSEREAL"] of Real := [55(1.0)]):
        offsetval (Array[0.."MAX_ASSEREAL"] of Real):
        typval (Array[0.."MAX_ASSEREAL"] of Int := [55(-1)]):
    """
    def __init__(self):
        self._defaults = {}
        self.boolval = [False] * (MAX_ASSEBOOL + 1)  # Array[0.."MAX_ASSEBOOL"] of Bool
        self._defaults['boolval'] = [False] * (MAX_ASSEBOOL + 1)
        self.intval = [-1] * (MAX_ASSEINT + 1)  # Array[0.."MAX_ASSEINT"] of Int := [8(-1), 1, 18(-1), 100, 2(0), 15(-1), 2(0), 2000, 6(-1), 2(0), 100, 7(-1), 2(0), 2(-1), 0, 2, 25(-1)]
        self._defaults['intval'] = [-1] * (MAX_ASSEINT + 1)
        self.realvalcfg = [0.0] * (MAX_ASSEREAL + 1)  # Array[0.."MAX_ASSEREAL"] of Real
        self._defaults['realvalcfg'] = [0.0] * (MAX_ASSEREAL + 1)
        self.realval = [0.0] * (MAX_ASSEREAL + 1)  # Array[0.."MAX_ASSEREAL"] of Real
        self._defaults['realval'] = [0.0] * (MAX_ASSEREAL + 1)
        self.fcval = [0.0] * (MAX_ASSEREAL + 1)  # Array[0.."MAX_ASSEREAL"] of Real := [55(1.0)]
        self._defaults['fcval'] = [0.0] * (MAX_ASSEREAL + 1)
        self.offsetval = [0.0] * (MAX_ASSEREAL + 1)  # Array[0.."MAX_ASSEREAL"] of Real
        self._defaults['offsetval'] = [0.0] * (MAX_ASSEREAL + 1)
        self.typval = [-1] * (MAX_ASSEREAL + 1)  # Array[0.."MAX_ASSEREAL"] of Int := [55(-1)]
        self._defaults['typval'] = [-1] * (MAX_ASSEREAL + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_AxisParam {fields}>"



class Type_Axis:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        prev_pos (Real):
        prev_vel (Real):
        curr_velist (Real):
        prev_velist (Real):
        velavg_buf (Array[0.."MAX_DT"] of Real):
        dsavg_buf (Array[0.."MAX_DT"] of Real):
        dsmsavg_buf (Array[0.."MAX_DT"] of Real):
        slave (Int):
        mov_debug (Int):
        ds (Real):
        ds_ms (Real):
        stop (Bool):
        stopping (Bool):
        started (Bool):
        timeout_enabled (Bool):
        t_start (Time):
        delta_t_start (Real):
        t_mov (Time):
        delta_t_mov (Real):
        curr_timeout (Int):
        slewrate_s_up (Real):
        slewrate_s_down (Real):
        val_input (Real):
        val_input_prev (Real):
        val_output (Real):
        val_output_prev (Real):
        pid_timer (TON_TIME):
        stat_sp_pos (Real):
        stat_sp_vel (Real):
        stat_sp_delta (Real):
        stat_sp_enable (Bool):
        stat_sp_intmode (Int):
        sp_pos (Real):
        prev_sp_pos (Real):
        sp_vel (Real):
        sp_vel_prev (Real):
        sp_delta (Real):
        sp_enable (Bool):
        interp_vmaster (Real):
        interp_vslave (Real):
        interp_dsmaster (Real):
        interp_dsslave (Real):
        interp_tmaster (Real):
        interp_tslave (Real):
        interp_rmaster (Real):
        interp_rslave (Real):
    """
    def __init__(self):
        self._defaults = {}
        self.prev_pos = 0.0  # Real
        self._defaults['prev_pos'] = 0.0
        self.prev_vel = 0.0  # Real
        self._defaults['prev_vel'] = 0.0
        self.curr_velist = 0.0  # Real
        self._defaults['curr_velist'] = 0.0
        self.prev_velist = 0.0  # Real
        self._defaults['prev_velist'] = 0.0
        self.velavg_buf = [0.0] * (MAX_DT + 1)  # Array[0.."MAX_DT"] of Real
        self._defaults['velavg_buf'] = [0.0] * (MAX_DT + 1)
        self.dsavg_buf = [0.0] * (MAX_DT + 1)  # Array[0.."MAX_DT"] of Real
        self._defaults['dsavg_buf'] = [0.0] * (MAX_DT + 1)
        self.dsmsavg_buf = [0.0] * (MAX_DT + 1)  # Array[0.."MAX_DT"] of Real
        self._defaults['dsmsavg_buf'] = [0.0] * (MAX_DT + 1)
        self.slave = -1  # Int
        self._defaults['slave'] = -1
        self.mov_debug = -1  # Int
        self._defaults['mov_debug'] = -1
        self.ds = 0.0  # Real
        self._defaults['ds'] = 0.0
        self.ds_ms = 0.0  # Real
        self._defaults['ds_ms'] = 0.0
        self.stop = False  # Bool
        self._defaults['stop'] = False
        self.stopping = False  # Bool
        self._defaults['stopping'] = False
        self.started = False  # Bool
        self._defaults['started'] = False
        self.timeout_enabled = False  # Bool
        self._defaults['timeout_enabled'] = False
        self.t_start = None  # Time
        self._defaults['t_start'] = None
        self.delta_t_start = 0.0  # Real
        self._defaults['delta_t_start'] = 0.0
        self.t_mov = None  # Time
        self._defaults['t_mov'] = None
        self.delta_t_mov = 0.0  # Real
        self._defaults['delta_t_mov'] = 0.0
        self.curr_timeout = -1  # Int
        self._defaults['curr_timeout'] = -1
        self.slewrate_s_up = 0.0  # Real
        self._defaults['slewrate_s_up'] = 0.0
        self.slewrate_s_down = 0.0  # Real
        self._defaults['slewrate_s_down'] = 0.0
        self.val_input = 0.0  # Real
        self._defaults['val_input'] = 0.0
        self.val_input_prev = 0.0  # Real
        self._defaults['val_input_prev'] = 0.0
        self.val_output = 0.0  # Real
        self._defaults['val_output'] = 0.0
        self.val_output_prev = 0.0  # Real
        self._defaults['val_output_prev'] = 0.0
        self.pid_timer = None  # TON_TIME
        self._defaults['pid_timer'] = None
        self.stat_sp_pos = 0.0  # Real
        self._defaults['stat_sp_pos'] = 0.0
        self.stat_sp_vel = 0.0  # Real
        self._defaults['stat_sp_vel'] = 0.0
        self.stat_sp_delta = 0.0  # Real
        self._defaults['stat_sp_delta'] = 0.0
        self.stat_sp_enable = False  # Bool
        self._defaults['stat_sp_enable'] = False
        self.stat_sp_intmode = -1  # Int
        self._defaults['stat_sp_intmode'] = -1
        self.sp_pos = 0.0  # Real
        self._defaults['sp_pos'] = 0.0
        self.prev_sp_pos = 0.0  # Real
        self._defaults['prev_sp_pos'] = 0.0
        self.sp_vel = 0.0  # Real
        self._defaults['sp_vel'] = 0.0
        self.sp_vel_prev = 0.0  # Real
        self._defaults['sp_vel_prev'] = 0.0
        self.sp_delta = 0.0  # Real
        self._defaults['sp_delta'] = 0.0
        self.sp_enable = False  # Bool
        self._defaults['sp_enable'] = False
        self.interp_vmaster = 0.0  # Real
        self._defaults['interp_vmaster'] = 0.0
        self.interp_vslave = 0.0  # Real
        self._defaults['interp_vslave'] = 0.0
        self.interp_dsmaster = 0.0  # Real
        self._defaults['interp_dsmaster'] = 0.0
        self.interp_dsslave = 0.0  # Real
        self._defaults['interp_dsslave'] = 0.0
        self.interp_tmaster = 0.0  # Real
        self._defaults['interp_tmaster'] = 0.0
        self.interp_tslave = 0.0  # Real
        self._defaults['interp_tslave'] = 0.0
        self.interp_rmaster = 0.0  # Real
        self._defaults['interp_rmaster'] = 0.0
        self.interp_rslave = 0.0  # Real
        self._defaults['interp_rslave'] = 0.0

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_Axis {fields}>"



class Type_IOParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        iotype (Int := -1): 0 = DI, 1 = AI, 2 = DO, 3 = AO, 4 = RI
        boolval (Array[0.."MAX_IOBOOL"] of Bool):
        intval (Array[0.."MAX_IOINT"] of Int := [9(-1)]):
        dintval (Array[0.."MAX_IODINT"] of DInt):
        realvalcfg (Array[0.."MAX_IOREAL"] of Real := [3(0.0), 3(1.0)]):
        realval (Array[0.."MAX_IOREAL"] of Real := [3(0.0), 3(1.0)]):
        exprintval (Array[0.."MAX_EXPRINT"] of Int := [25(-1)]): typ + (not, opnd, oper) x 8
        exprrealval (Array[0.."MAX_EXPROPER"] of Real):
    """
    def __init__(self):
        self._defaults = {}
        self.iotype = -1  # Int := -1 // 0 = DI, 1 = AI, 2 = DO, 3 = AO, 4 = RI
        self._defaults['iotype'] = -1
        self.boolval = [False] * (MAX_IOBOOL + 1)  # Array[0.."MAX_IOBOOL"] of Bool
        self._defaults['boolval'] = [False] * (MAX_IOBOOL + 1)
        self.intval = [-1] * (MAX_IOINT + 1)  # Array[0.."MAX_IOINT"] of Int := [9(-1)]
        self._defaults['intval'] = [-1] * (MAX_IOINT + 1)
        self.dintval = [-1] * (MAX_IODINT + 1)  # Array[0.."MAX_IODINT"] of DInt
        self._defaults['dintval'] = [-1] * (MAX_IODINT + 1)
        self.realvalcfg = [0.0] * (MAX_IOREAL + 1)  # Array[0.."MAX_IOREAL"] of Real := [3(0.0), 3(1.0)]
        self._defaults['realvalcfg'] = [0.0] * (MAX_IOREAL + 1)
        self.realval = [0.0] * (MAX_IOREAL + 1)  # Array[0.."MAX_IOREAL"] of Real := [3(0.0), 3(1.0)]
        self._defaults['realval'] = [0.0] * (MAX_IOREAL + 1)
        self.exprintval = [-1] * (MAX_EXPRINT + 1)  # Array[0.."MAX_EXPRINT"] of Int := [25(-1)] // typ + (not, opnd, oper) x 8
        self._defaults['exprintval'] = [-1] * (MAX_EXPRINT + 1)
        self.exprrealval = [0.0] * (MAX_EXPROPER + 1)  # Array[0.."MAX_EXPROPER"] of Real
        self._defaults['exprrealval'] = [0.0] * (MAX_EXPROPER + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_IOParam {fields}>"



class Type_ToolsetParam:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        boolval (Array[0.."MAX_TOOLSETBOOL"] of Bool):
        intval (Array[0.."MAX_TOOLSETINT"] of Int := [4(-1)]):
        realvalcfg (Array[0.."MAX_TOOLSETREAL"] of Real):
        realval (Array[0.."MAX_TOOLSETREAL"] of Real):
        fcval (Array[0.."MAX_TOOLSETREAL"] of Real := [20(1.0)]):
        offsetval (Array[0.."MAX_TOOLSETREAL"] of Real):
        typval (Array[0.."MAX_TOOLSETREAL"] of Int := [20(-1)]):
        output (Array[0.."MAX_TOOLSETOUTPUT"] of "Type_ToolsetOutputParam" := [([2(-1)], [()]), ([2(-1)], [()]), ([2(-1)], [()]), ([2(-1)], [()])]):
    """
    def __init__(self):
        self._defaults = {}
        self.boolval = [False] * (MAX_TOOLSETBOOL + 1)  # Array[0.."MAX_TOOLSETBOOL"] of Bool
        self._defaults['boolval'] = [False] * (MAX_TOOLSETBOOL + 1)
        self.intval = [-1] * (MAX_TOOLSETINT + 1)  # Array[0.."MAX_TOOLSETINT"] of Int := [4(-1)]
        self._defaults['intval'] = [-1] * (MAX_TOOLSETINT + 1)
        self.realvalcfg = [0.0] * (MAX_TOOLSETREAL + 1)  # Array[0.."MAX_TOOLSETREAL"] of Real
        self._defaults['realvalcfg'] = [0.0] * (MAX_TOOLSETREAL + 1)
        self.realval = [0.0] * (MAX_TOOLSETREAL + 1)  # Array[0.."MAX_TOOLSETREAL"] of Real
        self._defaults['realval'] = [0.0] * (MAX_TOOLSETREAL + 1)
        self.fcval = [0.0] * (MAX_TOOLSETREAL + 1)  # Array[0.."MAX_TOOLSETREAL"] of Real := [20(1.0)]
        self._defaults['fcval'] = [0.0] * (MAX_TOOLSETREAL + 1)
        self.offsetval = [0.0] * (MAX_TOOLSETREAL + 1)  # Array[0.."MAX_TOOLSETREAL"] of Real
        self._defaults['offsetval'] = [0.0] * (MAX_TOOLSETREAL + 1)
        self.typval = [-1] * (MAX_TOOLSETREAL + 1)  # Array[0.."MAX_TOOLSETREAL"] of Int := [20(-1)]
        self._defaults['typval'] = [-1] * (MAX_TOOLSETREAL + 1)
        self.output = None  # Array[0.."MAX_TOOLSETOUTPUT"] of "Type_ToolsetOutputParam" := [([2(-1)], [()]), ([2(-1)], [()]), ([2(-1)], [()]), ([2(-1)], [()])]
        self._defaults['output'] = None

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_ToolsetParam {fields}>"



class Type_LongString:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        c (Array[0.."DIM_STRINGHEADER"] of Char):
        ind (Int):
    """
    def __init__(self):
        self._defaults = {}
        self.c = [None] * (DIM_STRINGHEADER + 1)  # Array[0.."DIM_STRINGHEADER"] of Char
        self._defaults['c'] = [None] * (DIM_STRINGHEADER + 1)
        self.ind = -1  # Int
        self._defaults['ind'] = -1

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_LongString {fields}>"



class Type_DataLoggerBuffer:
    """
    Estratto da: PlcDataType.udt

    Attributes:
        Num (Int):
        InInd (Int):
        OutInd (Int):
        Class (Array[0.."MAX_DATALOGGER_BUFFER"] of Int):
        Cod (Array[0.."MAX_DATALOGGER_BUFFER"] of Int):
        Val (Array[0.."MAX_DATALOGGER_BUFFER"] of Int):
        Cnt (Array[0.."MAX_DATALOGGER_BUFFER"] of Int):
    """
    def __init__(self):
        self._defaults = {}
        self.Num = -1  # Int
        self._defaults['Num'] = -1
        self.InInd = -1  # Int
        self._defaults['InInd'] = -1
        self.OutInd = -1  # Int
        self._defaults['OutInd'] = -1
        self.Class = [-1] * (MAX_DATALOGGER_BUFFER + 1)  # Array[0.."MAX_DATALOGGER_BUFFER"] of Int
        self._defaults['Class'] = [-1] * (MAX_DATALOGGER_BUFFER + 1)
        self.Cod = [-1] * (MAX_DATALOGGER_BUFFER + 1)  # Array[0.."MAX_DATALOGGER_BUFFER"] of Int
        self._defaults['Cod'] = [-1] * (MAX_DATALOGGER_BUFFER + 1)
        self.Val = [-1] * (MAX_DATALOGGER_BUFFER + 1)  # Array[0.."MAX_DATALOGGER_BUFFER"] of Int
        self._defaults['Val'] = [-1] * (MAX_DATALOGGER_BUFFER + 1)
        self.Cnt = [-1] * (MAX_DATALOGGER_BUFFER + 1)  # Array[0.."MAX_DATALOGGER_BUFFER"] of Int
        self._defaults['Cnt'] = [-1] * (MAX_DATALOGGER_BUFFER + 1)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._defaults.keys()}

    def reset(self):
        for k, v in self._defaults.items():
            setattr(self, k, v)

    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)}" for k in self._defaults.keys())
        return f"<Type_DataLoggerBuffer {fields}>"


# ===== Costanti da: PLCTags.xlsx =====
STATO_INIT = 0
STATO_MAN = 1
STATO_AUTO = 2
STATO_DEVCONFIG = 3
COD_MANMOVE = 0
COD_END = 3010
COD_RESTART = 3020
COD_DELAY = 3040
COD_PAUSE = 3050
COD_LOOP = 3021
COD_REPEAT = 3030
COD_SETDO = 3060
COD_SETAO = 3070
COD_SETPV = 3080
COD_WAITDI = 3090
COD_WAITAIINC = 3100
COD_WAITAIDEC = 3110
COD_NOP = 3120
COD_PINCHX = 3130
COD_INFEED = 3140
COD_REVINFEED = 3142
COD_STARTPOS = 3150
COD_REVSTARTPOS = 3152
COD_RELEASE = 3160
DATA_INT = 1
DATA_REAL = 2
DATA_BOOL = 3  # non usato per ora
DATA_STRING = 4  # non usato nel PLC
SEQ_SYSTEM = 1
SEQ_PROG = 2
OBJ_DI = 0
OBJ_DO = 2
COD_CALL = 5000
OBJ_AI = 1
OBJ_AO = 3
COD_WAITAI = 3111
GE = 1
EQ = 0
LE = -1
INPUT_JS = 2  # Roundo
INPUT_SP = 3
INPUT_ONOFF = 1
COD_MOVE = 2
STATCLASS_CONTROL = 1
STATCLASS_AXIS = 2
STATCLASS_INTERPOLATION = 3
STATCLASS_RADIUS = 4
STATCLASS_WIZARD = 5
STATCLASS_SUBPROG = 6
FB_AI = 1
FB_DI = 2
FB_AHSC = 4
DEV_ADFWEBGW = 1
DEV_IMETM880 = 2
DEV_CANIO14 = 3
COD_SETROT = 3210
COD_AXIS = 1000
OBJ_K_INT = 4
OBJ_K_REAL = 5
OBJ_K_BOOL = 6
OBJ_K_STRING = 7
COD_RADIUS_A = 2010
COD_RADIUS_AB = 2011
COD_RADIUS_BC = 2020
COD_RADIUS_BIPOL = 2021
COD_WIZARD = 4000
COD_WIZARD_SINGLE1 = 4001
COD_WIZARD_SINGLE2 = 4002
COD_WIZARD_SINGLE3 = 4003
COD_WIZARD_SINGLE4 = 4004
COD_WIZARD_DOUBLE2 = 4005
COD_WIZARD_DOUBLE3 = 4006
COD_WIZARD_DOUBLE4 = 4007
COD_WIZARD_GENERIC = 4012
COD_INTERP = 6000
FB_INCENC = 6
COD_DROLLDOWN = 3206  # seq 6
COD_PINCH = 3205  # seq 5
COD_DROPENDDOWN = 3201  # seq 1
COD_DROPENDUP = 3202  # seq 2
COD_EJECTOROUT = 3203  # seq 3
OUTPUT_DIR = 2
OUTPUT_SEL = 1
ALARM_MSG = 0
ALARM_STOP = 1
OP_NONE = -1
OP_EQ = 0
OP_NE = 1
OP_LT = 2
OP_LE = 3
OP_GT = 4
OP_GE = 5
IN_DIGITAL = 0
IN_ANALOG = 1
IN_OGGTEC = 2
OUTPUT_DIRINV = 3
MAX_TICK = 2147483647
FB_AI2 = 7
PINCH_MECH = 4  # era 0
PINCH_PRESS = 1
PINCH_POS = 2
MACHTYPE_PASS = 1
MACHTYPE_PAS = 2
MACHTYPE_4HEL = 4
MACHTYPE_4HEP = 5
MACHTYPE_R = 6
UM_METRIC = 0
UM_IMP = 1
PIDTYPE_NONE = -1
PIDTYPE_TEMP = 1
PIDTYPE_COMPACT = 0
COD_PUSHROLLFW = 3207  # 3201 in wCNC2 - seq
COD_PUSHROLLBW = 3208  # 3202 in wCNC2 - seq
COD_PUSHROLLSTOP = 3209  # 3203 in wCNC2 - seq
MACHTYPE_HAV = 7
TEACHBIT_MEM = 0
TEACHBIT_MEMACK = 1
TEACHBIT_RESET = 2
TEACHBIT_RESETACK = 3
MISURA_LUNGH = 0
MISURA_PRESS = 1
MISURA_TEMP = 2
MISURA_VELPERC = 3
MISURA_YP = 4
MISURA_RAPP = 5
MISURA_VELLUNG = 6
MISURA_VELPRESS = 7
MISURA_AREA = 8
MISURA_ROT = 9
COD_FLOATINGON = 3211
COD_FLOATINGOFF = 3212
COD_EXTMEASON = 3213
COD_EXTMEASOFF = 3214
PROGOUT_RESET = 0
PROGOUT_SAVE = 1
PROGOUT_LOAD = 2
CALCTYPE_4 = 0
CALCTYPE_3 = 1
COD_SENSPOS = 3155
COD_CNTRESET0 = 3240
COD_CNTRESET1 = 3241
COD_CNTRESET2 = 3242
COD_CNTINC0 = 3243
COD_CNTINC1 = 3244
COD_CNTINC2 = 3245
COD_CNTDEC0 = 3246
COD_CNTDEC1 = 3247
COD_CNTDEC2 = 3248
COD_EJECTORIN = 3204  # seq 4
MAINT_CHECKSTARTED = 0
MAINT_CHECKTIME = 1  # usa MAINT_INT_MAXVAL anche a macchina spenta
MAINT_CHECKTIME2 = 3
COD_CHECK = 3156
CFG_STARTGETCONFIG = 1
CFG_GETSETTINGS = 2
CFG_GETCONFIG = 3
CFG_GETSYSPROG1 = 4
CFG_GETSYSPROG2 = 5
CFG_GETSYSPROG3 = 6
CFG_SETSETTINGS = 10
CFG_SETCONFIG = 11
CFG_NOCONFIG = 0
CALCTYPE_HAV = 2
MACHTYPE_RCMI = 8
MACHTYPE_4R = 9
SETTING_INT_UM = 0
SETTING_INT_LANG = 1
SETTING_INT_TIMEOUTPOWEROFF = 2
SETTING_BOOL_LOADMODE = 0  # era SETTING_BOOL_FEEDSIDE
SETTING_BOOL_FLAGGEO = 1  # era SETTING_BOOL_ORIENT
SETTING_BOOL_FLAGPROGMOD = 2
MISURA_E0 = 10  # era MISURA_VELTEMP
SETTiNG_INT_TOOLSET = 3
PID_REAL_KP = 0
PID_REAL_TD = 1
PID_REAL_TI = 2
PID_REAL_CRD = 3
PID_REAL_PONDP = 4
PID_REAL_PONDD = 5
PID_REAL_T = 6
INPUT_INT_TIPO = 0
INPUT_INT_TIPOMISURA = 1
INPUT_INT_ANAIND = 2
INPUT_INT_UPIND = 3
INPUT_INT_DOWNIND = 4
INPUT_INT_K = 5
INPUT_INT_UP2IND = 6
INPUT_INT_DOWN2IND = 7
INPUT_INT_K2 = 8
INPUT_DINT_VMIN = 0
INPUT_DINT_VMAX = 1
INPUT_DINT_VMIN2 = 2
INPUT_DINT_VMAX2 = 3
OUTPUT_INT_TIPO = 0
OUTPUT_INT_ANA1IND = 1
OUTPUT_INT_ANA2IND = 2
OUTPUT_INT_DIG1IND = 3
OUTPUT_INT_DIG2IND = 4
OUTPUT_DINT_SCALEMIN1 = 0
OUTPUT_DINT_SCALEMAX1 = 1
OUTPUT_DINT_SCALEMIN2 = 2
OUTPUT_DINT_SCALEMAX2 = 3
OUTPUT_REAL_VALMIN1 = 0
OUTPUT_REAL_VALMAX1 = 1
OUTPUT_REAL_VALMIN2 = 2
OUTPUT_REAL_VALMAX2 = 3
OUTPUT_REAL_VIN0 = 4
OUTPUT_REAL_VOUT0 = 5
OUTPUT_REAL_VIN1 = 6
OUTPUT_REAL_VOUT1 = 7
OUTPUT_REAL_VIN2 = 8
OUTPUT_REAL_VOUT2 = 9
OUTPUT_REAL_VIN3 = 10
OUTPUT_REAL_VOUT3 = 11
OUTPUT_REAL_VIN4 = 12
OUTPUT_REAL_VOUT4 = 13
OUTPUT_REAL_VIN5 = 14
OUTPUT_REAL_VOUT5 = 15
OUTPUT_REAL_V2IN0 = 16
OUTPUT_REAL_V2OUT0 = 17
OUTPUT_REAL_V2IN1 = 18
OUTPUT_REAL_V2OUT1 = 19
OUTPUT_REAL_V2IN2 = 20
OUTPUT_REAL_V2OUT2 = 21
OUTPUT_REAL_V2IN3 = 22
OUTPUT_REAL_V2OUT3 = 23
OUTPUT_REAL_V2IN4 = 24
OUTPUT_REAL_V2OUT4 = 25
OUTPUT_REAL_V2IN5 = 26
OUTPUT_REAL_V2OUT5 = 27
COD_AUTOMOVE = 1
INTMODE_NONE = -1
INTMODE_NOINTERP = 0
INTMODE_INTERP = 1
INTMODE_ONTHEFLY = 2  # non sincronizzato con gli altri movimenti
CFG_SETCANCONFIG = 7
IO_BOOL_BDEFVAL = 0
IO_BOOL_PROG = 1
IO_BOOL_SIM = 2
IO_BOOL_SIMVAL = 3
IO_INT_ADDRTYPE = 0  # Usato anche per CNT/TOT
IO_INT_ADDR1 = 1  # Usato anche per CNT/TOT
IO_INT_ADDR2 = 2  # Se 0 Real, se 1 DInt
IO_INT_NBYTES = 3  # era IDEFVAL (se <> 1 vale 2, per gestione default 0)
IO_INT_MEMIND = 6  # Non serve
IO_INT_MEMTYPE = 5
IO_INT_TIMEOUT = 7  # v.25.11 - TIMER TIMEOUT  TON > 0, TOF < 0
IO_INT_ININD = 8  # v.25.11 - TIMER: DI, DO:DI, AO:AI
IO_DINT_DDEFVAL = 0
IO_REAL_RDEFVAL = 0  # Se è un TOT/CNT può essere usato come FC
IO_REAL_DEADBAND = 1  # minimo valore per considerare la modifica
IO_REAL_TOTDELTAMAX = 2  # massimo valore per considerare la modifica
IO_DI = 0
IO_AI = 1
IO_DO = 2
IO_AO = 3
IO_INT_TIPOMISURA = 4  # spostato a 4 da 8 (ed eliminare 6,7,8)
MAINT_BOOL_CONFIG = 0
MAINT_BOOL_FREE = 1
MAINT_INT_CHECKTYPE = 0
MAINT_INT_MAXVAL = 1  # ore
MAINT_INT_YYYY = 2
MAINT_INT_MM = 3
MAINT_INT_DD = 4
MAINT_INT_HH = 5
MAINT_INT_NN = 6
MAINT_INT_COD = 7
IO_TYPE_PNET = 0
IO_TYPE_CAN = 1
IO_TYPE_SW = 2
IO_TYPE_CALC = 3
MAX_HEADER = 3
MAX_SETTINGSBOOL = 21
MAX_SETTINGSINT = 11  # era 9 in v.0.18
DIM_STRINGNAME = 32
MAX_HMIDI = 31  # v.0.23 - da 15
MAX_HMIAI = 15  # era 7
MAX_HMIDO = 7
MAX_HMIAO = 7
MAX_BYPASS = 11
MAX_SYSPRESS = 2
MAX_INPUT = 47
MAX_OUTPUT = 47
MAX_PID = 3
MAX_ASSE = 47
MAX_MOTORE = 7
DIM_STRINGUMNAME = 8
MAX_MAINT = 31  # era 15 prima di 6436
MAX_UM = 12  # aggiunti MISURA_GRAD e MISURA_NUM
MAX_PARAMSTRING = 3
MAX_IO = 623
MAX_DI = 207
MAX_AI = 111
MAX_DO = 127
MAX_AO = 47
MAX_INPUTINT = 14
MAX_INPUTDINT = 3
MAX_MAINTBOOL = 1
MAX_MAINTINT = 9
MAX_IOBOOL = 3
MAX_IOINT = 8
MAX_IODINT = 1
MAX_IOREAL = 3
MAX_OUTPUTINT = 13  # era 4 prima di CCIND - aggiunti addparam, act, enabs
MAX_OUTPUTDINT = 7  # era 3 prima di CCIND
MAX_OUTPUTREAL = 27
MAX_PIDREAL = 6
DIM_STRINGID = 5
MAX_TEACHSTAT = 52  # era 3 - aggiunto MAX_ASSE + 1 per Input + 1 per setrot
MAX_SEQ = 5
MAX_STAT = 249  # era 99
MAX_STATPARAM = 1999  # era 999
MAX_SEQSTACK = 9
CFG_GETIOTSETTINGS = 8
MAX_CONSOLE = 21
MAX_CPU = 60
MAX_CPUDATA = 125
MAX_CONSOLEDATA = 47
DIM_CONSOLEDATA = 48  # DIM_CONSOLE * 2 + 4
DIM_CPUDATA = 126  # DIM_CPU * 2 + 4
DIM_CONSOLE = 22
DIM_CPU = 61
MAX_SER_BOOL = 99
MAX_SER_INT1 = 99
MAX_SER_REAL = 999
MAX_SER_INT2 = 599
MAX_SER_INT3 = 999
SETTING_BOOL_FLAGSMALL = 3
MAX_TABSTATASSE = 13
IO_RI = 4  # Tipo per i valori calcolati (sempre Real)
MAX_RI = 127
IO_TYPE_FUNC_TOT = 4
IO_TYPE_FUNC_TOTAUTO = 5
IO_TYPE_FUNC_TOTMAN = 6
IO_TYPE_FUNC_DTOT = 7
IO_TYPE_FUNC_DTOTAUTO = 8
IO_TYPE_FUNC_DTOTMAN = 9
IO_TYPE_FUNC_TIME = 10
IO_TYPE_FUNC_TIMEAUTO = 11
IO_TYPE_FUNC_TIMEMAN = 12
IO_TYPE_FUNC_DTIME = 13
IO_TYPE_FUNC_DTIMEAUTO = 14
IO_TYPE_FUNC_DTIMEMAN = 15
IO_IND_TOT = 0  # IO_TYPE_* -  IO_TYPE_TOT
IO_IND_TOTAUTO = 1
IO_IND_TOTMAN = 2
IO_IND_DTOT = 3
IO_IND_DTOTAUTO = 4
IO_IND_DTOTMAN = 5
IO_IND_TIME = 6
IO_IND_TIMEAUTO = 7
IO_IND_TIMEMAN = 8
IO_IND_DTIME = 9
IO_IND_DTIMEAUTO = 10
IO_IND_DTIMEMAN = 11
MAX_IOTVARIABLES = 127
MAX_IOREF = 11
MAX_IFMEXC = 4
CFG_GETJOBS = 9
MAX_DATALOGGER = 5  # 8 se IMG
DATALOGGER_ALARMS = 0
DATALOGGER_MAINT = 1
DATALOGGER_JOBS = 2
DATALOGGER_EVENTS = 3  # bool - solo su evento
DATALOGGER_PERINT = 4  # dint - solo periodici
DATALOGGER_PERREAL = 5  # real - solo periodici
DATALOGGER_IMGBOOL = 6
DATALOGGER_IMGINT = 7
DATALOGGER_IMGREAL = 8
DATALOGGER_NONE = -1
MAX_DATALOGGER_EVENTS = 30
MAX_DATALOGGER_INT = 30
MAX_DATALOGGER_REAL = 30
DATALOGGER_TIMEOUT = 600000  # 10 minuti = 10 * 60 * 1000
MAX_DATALOGGER_BUFFER = 40
DATALOGGER_ALARM_CLASS = 1
DATALOGGER_MAINT_CLASS = 65
DATALOGGER_MAXRECCOUNTPER = 1000
DATALOGGER_MAXRECCOUNTEVT = 1000
IO_REAL_COEFFMULT = 3
CMD_NOP = 0
CMD_TOP = 1
CMD_PAGEUP = 2
CMD_LINEUP = 3
CMD_LINEDOWN = 4
CMD_PAGEDOWN = 5
CMD_BOTTOM = 6
CMD_NEW = 7
CMD_SAVE = 8
CMD_SAVEAS = 9
CMD_LOAD = 10
CMD_DELETE = 11
CMD_RESET = 12
CMD_INSERT = 13
ERR_EXISTINGPROGNAME = 1
ERR_INVALIDPROGNAME = 2
ERR_SELECTPROGRAM = 3
ERR_MAXNUMPROG = 4
MAX_DT = 99
COD_WIZARD_MULTI = 4008
COD_WIZARD_ELLIPSE = 4009  # non usato
COD_WIZARD_REBEND1 = 4010
COD_WIZARD_OPEN = 4013
COD_WIZARD_REBEND2 = 4011  # non usato
COD_WIZARD_CONE = 4014
ALARM_WARNING = 2
INPUT_INT_ACTIND = 9
INPUT_INT_ENABIND = 10
INPUT_INT_ENAB2IND = 11
INPUT_INT_ENAB3IND = 12
INPUT_BOOL_HOLDTORUNENAB = 0
INPUT_BOOL_FREE = 1
MAX_INPUTBOOL = 1
SAFETY_NONE = -1
SAFETY_EXT = 0  # NON USATA
SAFETY_INT = 1  # Schede Safety gestite da PLC Safety
SAFETY_PROG = 2  # NON USATA
STATO_SINGMOVE = 4
COD_MOVEUP = 3
COD_MOVEDOWN = 4
COD_MOVEUPTIMEOUT = 6
COD_MOVEDOWNTIMEOUT = 7
COD_STOP = 5
COD_SETDI = 3055
COD_RESETDI = 3056
MACHTYPE_HAV12 = 3
SETTING_INT_GREASETIMEOUT1 = 4
SETTING_INT_GREASETIMEOUT2 = 5
SETTING_INT_GREASENUMFEEDBACK = 6
GREASE_STAT_INIT = -1
GREASE_STAT_WAITINGFORSTART = 0
GREASE_STAT_STARTCYCLE = 1
GREASE_STAT_SEND = 2
GREASE_STAT_RECV = 3
GREASE_STAT_TEST = 4
GREASE_STAT_ERROR = 5
OUTPUT_SELSLOW = 4
CHECK_MANUAL = 0
CHECK_ARCHIMETER = 1
CHECK_EBKEYENCE = 2
CHECK_EBORBBEC = 3
COD_ALIGN = 3300
COD_ALIGNRESET = 3302
COD_WIZARD_WT = 4015
OUTPUT_ADV = 5
OUTPUT_PSLCAN = 6
OUTPUT_SELFL = 7
OUTPUT_SEL2PV = 8
IO_TYPE_NONE = -1
INPUT_INT_SUPIND = 13  # indice AI limite superiore valore
OUTPUT_INT_CCIND = 5
OUTPUT_DINT_SCALEMIN1H = 4
OUTPUT_DINT_SCALEMAX1H = 5
OUTPUT_DINT_SCALEMIN2H = 6
OUTPUT_DINT_SCALEMAX2H = 7
SETTING_INT_EYEBENDX1 = 7
SETTING_INT_EYEBENDX2 = 8
COD_RESETROT = 3215
COD_BEGINCYCLE = 3011
COD_ENDCYCLE = 3012
SETTING_BOOL_FLAGWTMOD = 4
OUTPUT_INT_ADDPARAM1 = 6
OUTPUT_INT_ADDPARAM2 = 7
OUTPUT_INT_ADDPARAM3 = 8
OUTPUT_INT_ADDPARAM4 = 9
MOTOR_BOOL_LS = 0  # Motore_LSVal
MOTOR_BOOL_TR = 1  # Motore_TRVal
MOTOR_BOOL_CMD = 2  # Motore_CmdVal
MOTOR_BOOL_STAT = 3  # Motore_StatVal
MOTOR_BOOL_LS2 = 4  # Motore_LS2Val
MOTOR_BOOL_CONFIG = 5  # Motore_Config
MOTOR_BOOL_SELECTABLE = 6  # Motore_Selectable
SETTING_BOOL_ALIGNSAS = 5
SETTING_BOOL_SIM = 6
SETTING_REAL_DEFSPEED = 12
SETTING_REAL_DEFINTERPSPEED = 13
SETTING_BOOL_DYNSIM = 7
SETTING_BOOL_DISABALARMS = 8
SETTING_BOOL_DISABDATALOGGER = 9
SETTING_BOOL_DEFSRENAB = 10  # Support Rolls
COD_REPEATEND = 3031
COD_APPLY = 3032
MAX_REPEAT = 2
CAN_IMET = 0
CAN_IFM = 1
CAN_PSLCAN = 2
MAX_CANNODE = 19
MAX_IFMNODE = 5  # era 4 prima di 6642
MAX_PSLCANNODE = 12
MAX_IFMOUT = 95
MAX_IFMCURROUT = 47
NUM_PSLCANFULLNODE = 11
NUM_PSLCANFLITENODE = 2
MAX_IFMVBB = 11
PINCH_NONE = 0
COD_PINCHP = 3131  # non gestibile singolarmente in HMI
IO_DINT_SIMVAL = 1  # val simulazione distinto da val default
MISURA_GRAD = 11
MISURA_NUM = 12
MOTOR_BOOL_CMD2 = 8  # Motore_CmdVal2
MOTOR_BOOL_CMD3 = 9  # Motore_CmdVal3
MOTOR_BOOL_CMD1 = 7  # Motore_CmdVal1
MOTOR_TYPE_M1 = 1
MOTOR_TYPE_M2 = 2
MOTOR_TYPE_M3 = 3
MOTOR_TYPE_M4 = 4
MOTOR_TYPE_M5 = 5
MOTOR_TYPE_M6 = 6
MOTOR_TYPE_M7 = 7
MOTOR_TYPE_M8 = 8
MOTOR_TYPE_RECYCLING = 9
MOTOR_TYPE_COOLING = 10
MOTOR_TYPE_HEATING = 11
MOTOR_TYPE_RT = 12
MOTOR_TYPE_RT2 = 13
MOTOR_TYPE_FLUSHING = 14
INPUT_INT_SEQID = 14  # indice SEQ sostituisce AXIS_FUNC
OUTPUT_INT_ACTIND = 10
OUTPUT_INT_ENABIND = 11
OUTPUT_INT_ENAB2IND = 12
OUTPUT_INT_ENAB3IND = 13
MAX_SETTINGSREAL = 17
SETTING_REAL_DEFTHICKNESS = 0  # LUNGH
SETTING_REAL_DEFWIDTH = 1  # LUNGH
SETTING_REAL_DEFFSE = 2  # LUNGH
SETTING_REAL_DEFYP = 3  # YP
SETTING_REAL_DEFE0 = 4  # E0
SETTING_REAL_DEFPINCHCOEFF = 5  # NUM
SETTING_REAL_DEFPINCHPRESSS = 6  # PRESS
SETTING_REAL_DEFADDITROT = 7  # LUNGH
SETTING_REAL_DEFTSDELTAUP = 8  # LUNGH
SETTING_REAL_DEFTSDELTADOWN = 9  # LUNGH
SETTING_BOOL_DEFVSENAB = 11  # Vertical Support
SETTING_BOOL_DEFSSENAB = 12  # Side Support
SETTING_BOOL_DEFHSENAB = 13  # Horizontal Support
SETTING_BOOL_DEFSENSENAB = 14  # Start Sensor
SETTING_BOOL_DEFDEENAB = 15  # Dropend
SETTING_BOOL_DEFPPENAB = 16  # Pressure Pinching
SETTING_REAL_DEFPREBENDSPEED = 14
SETTING_REAL_DEFEBSTART = 10  # NUM
SETTING_REAL_DEFEBEND = 11  # NUM
SETTING_INT_DEFEBHOLEIND = 9
SETTING_BOOL_DEFBWPB = 17  # Bw Prebend
SETTING_BOOL_DEFALIGNENAB = 18  # Alignment
SETTING_BOOL_DEFFPENAB = 19  # Final Position
SETTING_BOOL_DEFPROGTYPE = 20  # Axis/Radius
SETTING_REAL_DEFSTARTPOS = 15  # LUNGH
SETTING_BOOL_DEFQUALITYENAB = 21  # Quality
DIM_STRINGHEADER = 1024
SER_PROG = 0
SER_IO = 1
SER_STATUS = 2
SER_NONE = -1
SER_PARAMBOOL = 3
SER_PARAMINT = 4
SER_PARAMREAL = 5
SAFETY_PROGIN = 3  # Emgcy da Leuze e HoldToRun gestito da PLC
MAINT_INT_INDENAB = 8
MAINT_INT_INDDISAB = 9
COD_PRELOAD = 3216
COD_PRELOADOFF = 3217
SER_CONFIG = 6
SER_AXIS = 7
SER_FEEDBACK = 8
SER_INPUT = 9
SER_OUTPUT = 10
SER_ALARM = 11
SER_MAINT = 12
SER_MOTOR = 13
RT_C1 = 1  # 1 centratore MS - 6498
RT_C3 = 3  # 3 coppie centratori - 6436, 6266
RT_C4 = 4  # 4 coppie centratori - 6158
RT_C3S = 30  # 6321, 6322
PP_ROUNDO = 0  # come wCNC4
PP_FACCIN1 = 1  # 6293,6295,6498
PP_FACCIN2 = 2  # 6436
RESET_CALC = 0
RESET_PINCH = 1
RESET_CONST = 2
MAINT_CHECKSTARTED2 = 2  # usa MAINT_INT_NN per il primo controllo
MAINT_CHECKDATE = 4
MAX_SER_STEPS = 90
DATA_MAXBOOL = 31
DATA_MAXDINT = 103  # Dint per Int e DInt
DATA_MAXREAL = 31  # Era 19 in SynDiag
SYNDIAG_BOOL_AXIS1_MOVING = 12
SYNDIAG_BOOL_AXIS1_UP = 13
SYNDIAG_BOOL_AXIS1_DOWN = 14
SYNDIAG_BOOL_AXIS1_INFLSVAL = 16
SYNDIAG_BOOL_AXIS1_SUPLSVAL = 15
SYNDIAG_DINT_AXIS1_STATUS = 24
SYNDIAG_DINT_AXIS1_INDDISABLE = 25
SYNDIAG_DINT_AXIS1_OUTPUTVAL1_1 = 28
SYNDIAG_DINT_AXIS1_OUTPUTVAL1_2 = 29
SYNDIAG_DINT_AXIS1_OUTPUTVAL2_1 = 32
SYNDIAG_DINT_AXIS1_OUTPUTVAL2_2 = 33
SYNDIAG_DINT_AXIS1_OUTPUTVAL3_1 = 36
SYNDIAG_DINT_AXIS1_OUTPUTVAL3_2 = 37
SYNDIAG_REAL_AXIS1_POS = 0
SYNDIAG_REAL_AXIS1_SPEED = 1
SYNDIAG_REAL_AXIS1_DELTA = 2
SYNDIAG_REAL_AXIS1_VALINPUT = 3
SYNDIAG_REAL_AXIS1_VALOUTPUT = 4
SYNDIAG_DINT_AXIS1_OUTPUTVAL4_1 = 40
SYNDIAG_DINT_AXIS1_OUTPUTVAL4_2 = 41
SYNDIAG_DINT_AXIS1_INDPS = 26
SYNDIAG_DINT_AXIS1_INDDECOUP = 27
SYNDIAG_BOOL_BPVAL1 = 0
SYNDIAG_BOOL_BPVAL2 = 1
SYNDIAG_BOOL_BPVAL3 = 2
SYNDIAG_BOOL_BPVAL4 = 3
SYNDIAG_BOOL_BPVAL5 = 4
SYNDIAG_BOOL_BPVAL6 = 5
SYNDIAG_BOOL_BPVAL7 = 6
SYNDIAG_BOOL_BPVAL8 = 7
SYNDIAG_BOOL_BPVAL9 = 8
SYNDIAG_BOOL_BPVAL10 = 9
SYNDIAG_BOOL_BPVAL11 = 10
SYNDIAG_BOOL_BPVAL12 = 11
SYNDIAG_DINT_BPDISIND1 = 12
SYNDIAG_DINT_BPDISIND2 = 13
SYNDIAG_DINT_BPDISIND3 = 14
SYNDIAG_DINT_BPDISIND4 = 15
SYNDIAG_DINT_BPDISIND5 = 16
SYNDIAG_DINT_BPDISIND6 = 17
SYNDIAG_DINT_BPDISIND7 = 18
SYNDIAG_DINT_BPDISIND8 = 19
SYNDIAG_DINT_BPDISIND9 = 20
SYNDIAG_DINT_BPDISIND10 = 21
SYNDIAG_DINT_BPDISIND11 = 22
SYNDIAG_DINT_BPDISIND12 = 23
SYNDIAG_DINT_BPIND1 = 0
SYNDIAG_DINT_BPIND2 = 1
SYNDIAG_DINT_BPIND3 = 2
SYNDIAG_DINT_BPIND4 = 3
SYNDIAG_DINT_BPIND5 = 4
SYNDIAG_DINT_BPIND6 = 5
SYNDIAG_DINT_BPIND7 = 6
SYNDIAG_DINT_BPIND8 = 7
SYNDIAG_DINT_BPIND9 = 8
SYNDIAG_DINT_BPIND10 = 9
SYNDIAG_DINT_BPIND11 = 10
SYNDIAG_DINT_BPIND12 = 11
SYNDIAG_DINT_AXIS1_OUTPUTVAL1_3 = 30
SYNDIAG_DINT_AXIS1_OUTPUTVAL1_4 = 31
SYNDIAG_DINT_AXIS1_OUTPUTVAL2_3 = 34
SYNDIAG_DINT_AXIS1_OUTPUTVAL2_4 = 35
SYNDIAG_DINT_AXIS1_OUTPUTVAL3_3 = 38
SYNDIAG_DINT_AXIS1_OUTPUTVAL3_4 = 39
SYNDIAG_DINT_AXIS1_OUTPUTVAL4_3 = 42
SYNDIAG_DINT_AXIS1_OUTPUTVAL4_4 = 43
SYNDIAG_BOOL_AXIS2_DOWN = 19
SYNDIAG_BOOL_AXIS2_INFLSVAL = 21
SYNDIAG_BOOL_AXIS2_MOVING = 17
SYNDIAG_BOOL_AXIS2_SUPLSVAL = 20
SYNDIAG_BOOL_AXIS2_UP = 18
SYNDIAG_DINT_AXIS2_STATUS = 44
SYNDIAG_DINT_AXIS2_OUTPUTVAL4_4 = 63
SYNDIAG_DINT_AXIS2_OUTPUTVAL4_3 = 62
SYNDIAG_DINT_AXIS2_OUTPUTVAL4_2 = 61
SYNDIAG_DINT_AXIS2_OUTPUTVAL4_1 = 60
SYNDIAG_DINT_AXIS2_OUTPUTVAL3_4 = 59
SYNDIAG_DINT_AXIS2_OUTPUTVAL3_3 = 58
SYNDIAG_DINT_AXIS2_OUTPUTVAL3_2 = 57
SYNDIAG_DINT_AXIS2_OUTPUTVAL3_1 = 56
SYNDIAG_DINT_AXIS2_OUTPUTVAL2_4 = 55
SYNDIAG_DINT_AXIS2_OUTPUTVAL2_3 = 54
SYNDIAG_DINT_AXIS2_OUTPUTVAL2_2 = 53
SYNDIAG_DINT_AXIS2_OUTPUTVAL2_1 = 52
SYNDIAG_DINT_AXIS2_OUTPUTVAL1_4 = 51
SYNDIAG_DINT_AXIS2_OUTPUTVAL1_3 = 50
SYNDIAG_DINT_AXIS2_OUTPUTVAL1_2 = 49
SYNDIAG_DINT_AXIS2_OUTPUTVAL1_1 = 48
SYNDIAG_DINT_AXIS2_INDPS = 46
SYNDIAG_DINT_AXIS2_INDDISABLE = 45
SYNDIAG_DINT_AXIS2_INDDECOUP = 47
SYNDIAG_REAL_AXIS2_POS = 5
SYNDIAG_REAL_AXIS2_SPEED = 6
SYNDIAG_REAL_AXIS2_DELTA = 7
SYNDIAG_REAL_AXIS2_VALINPUT = 8
SYNDIAG_REAL_AXIS2_VALOUTPUT = 9
SYNDIAG_BOOL_AXIS3_MOVING = 22
SYNDIAG_BOOL_AXIS3_UP = 23
SYNDIAG_BOOL_AXIS3_DOWN = 24
SYNDIAG_BOOL_AXIS3_INFLSVAL = 25
SYNDIAG_BOOL_AXIS3_SUPLSVAL = 26
SYNDIAG_BOOL_AXIS4_MOVING = 27
SYNDIAG_BOOL_AXIS4_UP = 28
SYNDIAG_BOOL_AXIS4_DOWN = 29
SYNDIAG_BOOL_AXIS4_INFLSVAL = 30
SYNDIAG_BOOL_AXIS4_SUPLSVAL = 31
SYNDIAG_REAL_AXIS3_POS = 10
SYNDIAG_REAL_AXIS3_SPEED = 11
SYNDIAG_REAL_AXIS3_DELTA = 12
SYNDIAG_REAL_AXIS3_VALINPUT = 13
SYNDIAG_REAL_AXIS3_VALOUTPUT = 14
SYNDIAG_REAL_AXIS4_POS = 15
SYNDIAG_REAL_AXIS4_SPEED = 16
SYNDIAG_REAL_AXIS4_DELTA = 17
SYNDIAG_REAL_AXIS4_VALINPUT = 18
SYNDIAG_REAL_AXIS4_VALOUTPUT = 19
SYNDIAG_DINT_AXIS3_INDDECOUP = 67
SYNDIAG_DINT_AXIS3_INDDISABLE = 65
SYNDIAG_DINT_AXIS3_INDPS = 66
SYNDIAG_DINT_AXIS3_OUTPUTVAL1_1 = 68
SYNDIAG_DINT_AXIS3_OUTPUTVAL1_2 = 69
SYNDIAG_DINT_AXIS3_OUTPUTVAL1_3 = 70
SYNDIAG_DINT_AXIS3_OUTPUTVAL1_4 = 71
SYNDIAG_DINT_AXIS3_OUTPUTVAL2_1 = 72
SYNDIAG_DINT_AXIS3_OUTPUTVAL2_2 = 73
SYNDIAG_DINT_AXIS3_OUTPUTVAL2_3 = 74
SYNDIAG_DINT_AXIS3_OUTPUTVAL2_4 = 75
SYNDIAG_DINT_AXIS3_OUTPUTVAL3_1 = 76
SYNDIAG_DINT_AXIS3_OUTPUTVAL3_2 = 77
SYNDIAG_DINT_AXIS3_OUTPUTVAL3_3 = 78
SYNDIAG_DINT_AXIS3_OUTPUTVAL3_4 = 79
SYNDIAG_DINT_AXIS3_OUTPUTVAL4_1 = 80
SYNDIAG_DINT_AXIS3_OUTPUTVAL4_2 = 81
SYNDIAG_DINT_AXIS3_OUTPUTVAL4_3 = 82
SYNDIAG_DINT_AXIS3_OUTPUTVAL4_4 = 83
SYNDIAG_DINT_AXIS3_STATUS = 64
SYNDIAG_DINT_AXIS4_INDDECOUP = 87
SYNDIAG_DINT_AXIS4_INDDISABLE = 85
SYNDIAG_DINT_AXIS4_INDPS = 86
SYNDIAG_DINT_AXIS4_OUTPUTVAL1_1 = 88
SYNDIAG_DINT_AXIS4_OUTPUTVAL1_2 = 89
SYNDIAG_DINT_AXIS4_OUTPUTVAL1_3 = 90
SYNDIAG_DINT_AXIS4_OUTPUTVAL1_4 = 91
SYNDIAG_DINT_AXIS4_OUTPUTVAL2_1 = 92
SYNDIAG_DINT_AXIS4_OUTPUTVAL2_2 = 93
SYNDIAG_DINT_AXIS4_OUTPUTVAL2_3 = 94
SYNDIAG_DINT_AXIS4_OUTPUTVAL2_4 = 95
SYNDIAG_DINT_AXIS4_OUTPUTVAL3_1 = 96
SYNDIAG_DINT_AXIS4_OUTPUTVAL3_2 = 97
SYNDIAG_DINT_AXIS4_OUTPUTVAL3_3 = 98
SYNDIAG_DINT_AXIS4_OUTPUTVAL3_4 = 99
SYNDIAG_DINT_AXIS4_OUTPUTVAL4_1 = 100
SYNDIAG_DINT_AXIS4_OUTPUTVAL4_2 = 101
SYNDIAG_DINT_AXIS4_OUTPUTVAL4_3 = 102
SYNDIAG_DINT_AXIS4_OUTPUTVAL4_4 = 103
SYNDIAG_DINT_AXIS4_STATUS = 84
SYNDIAG_AXIS_NUMBOOL = 5
SYNDIAG_AXIS_NUMDINT = 20
SYNDIAG_AXIS_NUMREAL = 5
SYNDIAG_NUMAXIS = 4
SETTING_REAL_DEFMININTERPROT = 16
SETTING_REAL_DEFMININTERPMOV = 17
RT_NONE = -1
SER_PARAMMAIN = 14
SER_PARAMGEO = 15
SER_PARAMLAT = 16
SER_PARAMALIGN = 17
SER_PARAMCHECK = 18  # era SER_PARAMEB
SER_PARAMBP = 19
SER_PARAMGREASE = 20
SER_PARAMPINCH = 21
SER_RC = 22  # era SER_PARAMARCHIMETER
SETTING_INT_ARCHIMETERCOM = 10
SETTING_INT_ARCHIMETERL = 11
SER_PARAMSAFETY = 23
SER_SETTINGS = 24
INTMODE_NOSTOP = 3  # non rallenta alla fine del movimento
ALARM_SAFETY = 3
INPUT_JS4 = 4  # JS con 4 velocità fisse (RC grande)
MOTOR_BOOL_TR2 = 10  # Motore_TR2Val
MOTOR_BOOL_STARTING = 11  # Motore_StartingVal
ALARM_SAFETYSTOP = 4
RC_NONE = 0
RC_STD = 1
RC_BIG = 2
RC_SMALL = 3
SER_CAN = 25  # era SER_IFM
SER_TOOLSET = 26
MAX_EXPRINT = 24  # 8 x 3 + 1
MAX_EXPROPER = 7  # = MAX_EXPRREAL
IO_SYSTYPE_INDEX = 0
IO_SYSTYPE_AXIS = 1
IO_SYSTYPE_FEEDBACK = 2
IO_SYSTYPE_INPUT = 3
IO_SYSTYPE_OUTPUT = 4
IO_SYSTYPE_MOTOR = 5
IO_SYSTYPE_PID = 6
IO_SYSTYPE_TOOLSET = 7
IO_SYSTYPE_ALARM = 8
IO_SYSTYPE_MAINT = 9
IO_SYSAXIS_MOVING = 0
IO_SYSAXIS_UP = 1
IO_SYSAXIS_DOWN = 2
IO_SYSAXIS_MAX = 3
IO_SYSAXIS_MIN = 4
IO_SYSAXIS_SUPLS = 5
IO_SYSAXIS_INFLS = 6
IO_SYSAXIS_HH = 7
IO_SYSAXIS_H = 8
IO_SYSAXIS_L = 9
IO_SYSAXIS_LL = 10
IO_SYSAXIS_H0 = 11
IO_SYSAXIS_L0 = 12
IO_SYSAXIS_SAF = 13
IO_SYSAXIS_ALTFB = 14
IO_SYSAXIS_NONE = -1
IO_SYSFB_NONE = -1
IO_SYSFB_ERR = 0
IO_SYSFB_RESET = 1
IO_SYSINPUT_NONE = -1
IO_SYSINPUT_ACT = 0
IO_SYSINPUT_ENAB1 = 1
IO_SYSINPUT_ENAB2 = 2
IO_SYSINPUT_ENAB3 = 3
IO_SYSOUTPUT_NONE = -1
IO_SYSOUTPUT_ACT = 0
IO_SYSOUTPUT_ENAB1 = 1
IO_SYSOUTPUT_ENAB2 = 2
IO_SYSOUTPUT_ENAB3 = 3
IO_SYSMOTOR_NONE = -1
IO_SYSMOTOR_STAT = 0
IO_SYSMOTOR_CMD = 1
IO_SYSMOTOR_STOP = 2
IO_SYSMOTOR_START = 3
IO_SYSMOTOR_TR = 4
IO_SYSMOTOR_TR2 = 5
IO_SYSMOTOR_CMD1 = 6
IO_SYSMOTOR_CMD2 = 7
IO_SYSMOTOR_CMD3 = 8
IO_SYSMOTOR_STARTING = 9
IO_SYSMOTOR_SEL = 10
IO_SYSMOTOR_SEQ = 11
IO_SYSMOTOR_OPT = 12
IO_SYSMOTOR_DEF = 13
IO_SYSALARM_NONE = -1
IO_SYSALARM_VAL = 0
IO_SYSALARM_ENAB = 1
IO_SYSALARM_DISAB = 2
IO_SYSALARM_REQ = 3
IO_SYSALARM_ACK = 4
IO_SYSALARM_IN = 5
IO_SYSMAINT_NONE = -1
IO_SYSMAINT_VAL = 0
IO_SYSMAINT_ENAB = 1
IO_SYSMAINT_DISAB = 2
IO_SYSAXIS_BAD = 15
IO_SYSAXIS_TILT = 16
IO_SYSAXIS_P1UP = 17
IO_SYSAXIS_P1DOWN = 18
IO_SYSAXIS_P2UP = 19
IO_SYSAXIS_P2DOWN = 20
IO_SYSINPUT_ENAB = 4
IO_SYSOUTPUT_ENAB = 4
IO_SYSAXIS_SLOW = 21
IO_SYSAXIS_FAST = 22
IO_SYSTOOLSET_NONE = -1
IO_SYSTOOLSET_SEL = 0
AO_PRIORITY_FIRST = -1
AO_PRIORITY_LAST = 0
AO_PRIORITY_MIN = 1
AO_PRIORITY_MAX = 2
FB_RHSC = 3
SER_PARAMROLLCHANGE = 27
SER_RESET1 = 28  # Init RI NBytes, Timeout = -1 (Enab, Reset)
SER_RESET2 = 29
SER_RESET3 = 30
SER_RESET4 = 31
SER_RESET5 = 32
OUTPUT_ATV340 = 9
IO_EXPR_NONE = -1
IO_EXPR_VAL = 0
IO_EXPR_NOTVAL = 1
IO_EXPR_AIEQ0 = 2
IO_EXPR_AINE0 = 3
IO_EXPR_AIGT0 = 4
IO_EXPR_AIGE0 = 5
IO_EXPR_AILT0 = 6
IO_EXPR_AILE0 = 7
IO_EXPR_RIEQ0 = 8
IO_EXPR_RINE0 = 9
IO_EXPR_RIGT0 = 10
IO_EXPR_RIGE0 = 11
IO_EXPR_RILT0 = 12
IO_EXPR_RILE0 = 13
MAX_EXPRREAL = 7
IO_EXPR_AI = 20
IO_EXPR_ABSAI = 21
IO_EXPR_RI = 30
IO_EXPR_ABSRI = 31
IO_EXPR_K = 40
IO_EXPR_KUM = 41
IO_EXPR_OPOR = 1
IO_EXPR_OPAND = 0
IO_EXPR_OPPLUS = 2
IO_EXPR_OPMINUS = 3
IO_EXPR_OPMULT = 4
IO_EXPR_OPDIV = 5
HMIPAGE_MAN = 100  # no LOCAL pages
HMIPAGE_AUTO = 200  # no LOCAL pages
HMIPAGE_TABLE = 300  # no LOCAL pages
HMIPAGE_EXPLORER = 400
HMIPAGE_PROGRAM = 500
HMIPAGE_SETTINGS = 600
HMIPAGE_DIAG = 700
HMIPAGE_CORR = 800
HMIPAGE_CONFIG = 1000
HMIPAGE_MAN_PLATEROLLS = 101
HMIPAGE_MAN_RTC1LEFT = 102
HMIPAGE_MAN_RTC1RIGHT = 103
HMIPAGE_MAN_RTC3LEFT = 104
HMIPAGE_MAN_RTC3RIGHT = 105
HMIPAGE_MAN_SECTIONROLLS = 106
HMIPAGE_AUTO_MOVEPLATEROLLS = 201
HMIPAGE_AUTO_RTC1LEFT = 202
HMIPAGE_AUTO_RTC1RIGHT = 203
HMIPAGE_AUTO_RTC3LEFT = 204
HMIPAGE_AUTO_RTC3RIGHT = 205
HMIPAGE_AUTO_CONTROL = 220
HMIPAGE_AUTO_CONTROLALIGN = 221
HMIPAGE_AUTO_RADIUS = 230
HMIPAGE_AUTO_MOVESECTIONROLLS = 206
HMIPAGE_TABLE_MET = 301
HMIPAGE_TABLE_IMP = 302
HMIPAGE_TABLE_SIMMET = 303
HMIPAGE_TABLE_SIMIMP = 304
HMIPAGE_TABLE_SMALLMET = 305
HMIPAGE_TABLE_SMALLIMP = 306
HMIPAGE_EXPLORER_MODELESS = 401
HMIPAGE_EXPLORER_MODAL = 402
HMIPAGE_EXPLORER_MODIFY = 403
HMIPAGE_EXPLORER_IMPORT = 404
HMIPAGE_EXPLORER_IMPORTALL = 405
HMIPAGE_PROGRAM_POSITIONS = 501
HMIPAGE_PROGRAM_PRINT = 502
HMIPAGE_PROGRAM_RESET = 503
HMIPAGE_PROGRAM_TUNING = 504
HMIPAGE_PROGRAM_PROPMAIN = 510
HMIPAGE_PROGRAM_PROPAUTOCORR = 511
HMIPAGE_PROGRAM_PROPCAPACITY = 512
HMIPAGE_PROGRAM_PROPLOADER = 513
HMIPAGE_PROGRAM_PROPMAT = 514
HMIPAGE_PROGRAM_PROPSAVE = 515
HMIPAGE_PROGRAM_PROPYP = 516
HMIPAGE_PROGRAM_PROPYPCUSTOM = 517
HMIPAGE_PROGRAM_PROPADVPLATEROLLS = 520
HMIPAGE_PROGRAM_PROPADVSECROLLS = 521
HMIPAGE_PROGRAM_SHAPEGEN = 530
HMIPAGE_PROGRAM_SHAPECIRC = 531
HMIPAGE_PROGRAM_SHAPECONE = 532
HMIPAGE_PROGRAM_SHAPEPOLY = 533
HMIPAGE_PROGRAM_SHAPEREBEND = 534
HMIPAGE_PROGRAM_SHAPEREBEND2 = 535
HMIPAGE_PROGRAM_SHAPETAB = 536
HMIPAGE_PROGRAM_STATCONVERT = 540
HMIPAGE_PROGRAM_STATDELETE = 541
HMIPAGE_PROGRAM_STATMODCONTROL = 542
HMIPAGE_PROGRAM_STATMODRADIUS = 543
HMIPAGE_PROGRAM_MATMODIFY = 550
HMIPAGE_PROGRAM_MATTABLEBF = 551
HMIPAGE_PROGRAM_MATMODPOS = 552
HMIPAGE_PROGRAM_TOOLSETMOD = 560
HMIPAGE_PROGRAM_WTSECTION = 570
HMIPAGE_PROGRAM_WTMAIN = 571
HMIPAGE_PROGRAM_WTMOD = 572
HMIPAGE_SETTINGS_DEFADV = 601
HMIPAGE_SETTINGS_DEFMAT = 602
HMIPAGE_SETTINGS_LUB = 603
HMIPAGE_SETTINGS_OPER = 604
HMIPAGE_SETTINGS_RC = 605
HMIPAGE_SETTINGS_START = 606
HMIPAGE_SETTINGS_USERS = 607
HMIPAGE_SETTINGS_LUBBIG = 608
HMIPAGE_SETTINGS_SENSOR = 609
HMIPAGE_CORR_AUTO = 801
HMIPAGE_CORR_MAN = 802
HMIPAGE_DIAG_ADVINV = 701
HMIPAGE_DIAG_ALARMS = 702
HMIPAGE_DIAG_ALARMSHIST = 703
HMIPAGE_DIAG_MAINT = 704
HMIPAGE_DIAG_MAINTHIST = 705
HMIPAGE_DIAG_MAINTRESET = 706
HMIPAGE_DIAG_PLC = 707
HMIPAGE_DIAG_IFM = 710
HMIPAGE_DIAG_PSLCAN = 708
HMIPAGE_DIAG_SYNAXIS = 720
HMIPAGE_DIAG_SYNDE = 721
HMIPAGE_DIAG_SYNPLATEROLLS = 722
HMIPAGE_DIAG_SYNC1LEFT = 723
HMIPAGE_DIAG_SYNC1RIGHT = 724
HMIPAGE_DIAG_SYNC3LEFT = 725
HMIPAGE_DIAG_SYNC3RIGHT = 726
HMIPAGE_DIAG_SYNSECTIONROLLS = 727
HMIPAGE_INFO_CAPACITY = 750  # potrebbero essere DIAG invece di INFO
HMIPAGE_INFO_EM = 751
HMIPAGE_INFO_MACHINE = 752
HMIPAGE_INFO_MAIN = 753
HMIPAGE_INFO_PGSX = 754
HMIPAGE_JOB_LIST = 580
HMIPAGE_JOB_QUALITY = 581
HMIPAGE_JOB_SET = 582
HMIPAGE_ARCHIMETER_RADIUS = 810
HMIPAGE_EYEBEND_KEYENCE = 820
HMIPAGE_START = 150
HMIPAGE_SHUTDOWN = 151
HMIPAGE_TELESERVICE = 152
HMIPAGE_CONFIG_ALARMCURR = 1001
HMIPAGE_CONFIG_ALARMLIST = 1002
HMIPAGE_CONFIG_AXES0 = 1010
HMIPAGE_CONFIG_AXES1 = 1011
HMIPAGE_CONFIG_AXES2 = 1012
HMIPAGE_CONFIG_AXES3 = 1013
HMIPAGE_CONFIG_AXES4 = 1014
HMIPAGE_CONFIG_AXES5 = 1015
HMIPAGE_CONFIG_AXES6 = 1016
HMIPAGE_CONFIG_CURRBP = 1020
HMIPAGE_CONFIG_CURRCONTROL = 1021
HMIPAGE_CONFIG_CURRFB = 1022
HMIPAGE_CONFIG_CURRINPUT = 1023
HMIPAGE_CONFIG_CURRMAIN = 1024
HMIPAGE_CONFIG_CURROUTPUT = 1025
HMIPAGE_CONFIG_CURRPRESS = 1026
HMIPAGE_CONFIG_CURRRADIODISPLAY = 1027
HMIPAGE_CONFIG_CURRSAFETY = 1028
HMIPAGE_CONFIG_BROWSERPLC = 1040
HMIPAGE_CONFIG_BROWSER2 = 1041
HMIPAGE_CONFIG_CALC = 1042
HMIPAGE_CONFIG_DEBUG = 1043
HMIPAGE_CONFIG_DIAGRC = 1044
HMIPAGE_CONFIG_DIAGSYSTEM = 1045
HMIPAGE_CONFIG_IFM = 1050
HMIPAGE_CONFIG_IOCURR = 1400  # era 1060
HMIPAGE_CONFIG_IOLIST = 1410  # era 1061
HMIPAGE_CONFIG_IOSEL = 1420  # era 1062
HMIPAGE_CONFIG_DIEXPR = 1430  # era 1063 - era IOEXPR
HMIPAGE_CONFIG_MAIN = 1070
HMIPAGE_CONFIG_MAINTCURR = 1080
HMIPAGE_CONFIG_MAINTLIST = 1081
HMIPAGE_CONFIG_MOTORCURR = 1090
HMIPAGE_CONFIG_MOTORLIST = 1091
HMIPAGE_CONFIG_OBJLIST = 1100
HMIPAGE_CONFIG_PARAMS0 = 1110
HMIPAGE_CONFIG_PARAMS1 = 1111
HMIPAGE_CONFIG_PARAMS2 = 1112
HMIPAGE_CONFIG_PARAMS3 = 1113
HMIPAGE_CONFIG_PARAMS4 = 1114
HMIPAGE_CONFIG_PARAMSBP = 1120
HMIPAGE_CONFIG_PARAMSCHECK = 1121
HMIPAGE_CONFIG_PARAMSGEO = 1122
HMIPAGE_CONFIG_PARAMSGREASE = 1123
HMIPAGE_CONFIG_PARAMSGREASEIN = 1124
HMIPAGE_CONFIG_PARAMSGREASEOUT = 1125
HMIPAGE_CONFIG_PARAMSLAT = 1126
HMIPAGE_CONFIG_PARAMSMAIN = 1127
HMIPAGE_CONFIG_PARAMSMAINCMD = 1128
HMIPAGE_CONFIG_PARAMSMAINMODE = 1129
HMIPAGE_CONFIG_PARAMSMAINRSM = 1130
HMIPAGE_CONFIG_PARAMSMAINSEL = 1131
HMIPAGE_CONFIG_PARAMSMAINSTATUS = 1132
HMIPAGE_CONFIG_PARAMSPINCH = 1133
HMIPAGE_CONFIG_PARAMSRCIN = 1134
HMIPAGE_CONFIG_PARAMSRCOUT = 1135
HMIPAGE_CONFIG_PARAMSROLLCHANGE = 1136
HMIPAGE_CONFIG_PARAMSRT = 1137
HMIPAGE_CONFIG_PARAMSSAFETY = 1138
HMIPAGE_CONFIG_FUNIND = 1140
HMIPAGE_CONFIG_ROLLCHANGE = 1150
HMIPAGE_CONFIG_SINGMOVALL = 1200
HMIPAGE_CONFIG_SINGMOVPLATEROLLS = 1201
HMIPAGE_CONFIG_SINGMOVRTC1LEFT = 1202
HMIPAGE_CONFIG_SINGMOVRTC1RIGHT = 1203
HMIPAGE_CONFIG_SINGMOVRTC3LEFT = 1204
HMIPAGE_CONFIG_SINGMOVRTC3RIGHT = 1205
HMIPAGE_CONFIG_SINGMOVSECTIONROLLS = 1206
HMIPAGE_CONFIG_USERS = 1300
HMIPAGE_CONFIG_IOCURRDI = 1400
HMIPAGE_CONFIG_IOCURRAI = 1401
HMIPAGE_CONFIG_IOCURRDO = 1402
HMIPAGE_CONFIG_IOCURRAO = 1403
HMIPAGE_CONFIG_IOCURRRI = 1404
HMIPAGE_CONFIG_IOLISTDI = 1410
HMIPAGE_CONFIG_IOLISTAI = 1411
HMIPAGE_CONFIG_IOLISTDO = 1412
HMIPAGE_CONFIG_IOLISTAO = 1413
HMIPAGE_CONFIG_IOLISTRI = 1414
HMIPAGE_CONFIG_IOSELDI = 1420
HMIPAGE_CONFIG_IOSELAI = 1421
HMIPAGE_CONFIG_IOSELDO = 1422
HMIPAGE_CONFIG_IOSELAO = 1423
HMIPAGE_CONFIG_IOSELRI = 1424
HMIPAGE_CONFIG_IOEXPRDI = 1430
HMIPAGE_CONFIG_IOEXPRAI = 1431
HMIPAGE_CONFIG_IOEXPRDO = 1432
HMIPAGE_CONFIG_IOEXPRAO = 1433
HMIPAGE_CONFIG_IOEXPRRI = 1434
HMIPAGE_CONFIG_RIEXPR = 1431
TELESERVICE_NOREQ = 0
TELESERVICE_REQ_FACCIN = 1
TELESERVICE_NONE = -1
TELESERVICE_REQ_ROUNDO = 2
TELESERVICE_ACK = 3
TELESERVICE_NACK = 4
HMIDI_SETRX = 0
HMIDI_TESTDI = 1  # *
HMIDI_TESTDI2 = 2  # *
HMIDI_CYCLEMODE = 3
HMIDI_TEACHMODE = 4
HMIDI_FASTROLLS = 5
HMIDI_MAINTRESET = 6
HMIDI_PINCHTYPE = 7
HMIDI_PRELUP = 8
HMIDI_PRELDOWN = 9
HMIDI_EBIN = 10
HMIDI_EBOUT = 11
HMIDI_SHOCKABS = 12
HMIDI_ROTRTCOUP = 13
HMIDI_TTCOUP = 14
HMIDI_PRELCOUP = 15
HMIDI_A1ENAB = 16
HMIDI_B1ENAB = 17
HMIDI_SASOUT = 18
HMIDI_SASIN = 19
HMIDI_UNBALLEFT = 20
HMIDI_UNBALRIGHT = 21
HMIDI_FASTROT = 22
HMIDI_CHROLLMODE = 23
HMIDI_TILTDISAB = 24
HMIDI_SAFRESET = 25
HMIDI_FASTRT = 26
HMIDI_TILTUP = 27
HMIDI_TILTDOWN = 28
HMIDI_TABLELIFTUP = 29
HMIDI_TABLELIFTDOWN = 30
HMIAI_SETRX = 0
HMIAI_PINCHSP = 1
HMIAI_PINCHSPSLAVE = 2
HMIAI_ROLLSGUIDESPEED = 3
HMIAI_ROTSPEED = 4
HMIAI_COUNTER = 5
HMIAI_CYCLETIME = 6
HMIAI_TESTAI = 7  # *
HMIAI_PINCHOFFSET = 8
HMIAI_VERTPOS = 9
HMIAI_RTSPEED = 10
OUTPUT_SEL4PV = 10
MAX_IFMTYPE = 16  # tipi 1-17
MAX_IFMOUTTYPE = 271  # 16 out * 17 tipi - 1
MAX_CANNODEINT = 2
CANNODE_INT_TYPE = 0
CANNODE_INT_FREQ = 1
CANNODE_INT_VAL = 2
MAX_IFMEXCINT = 3
IFMEXC_INT_ID = 0
IFMEXC_INT_NOUT = 1
IFMEXC_INT_FREQ = 2
IFMEXC_INT_VAL = 3
MAX_INVERTER = 0
MAX_INVERTERWRITEBOOL = 15
MAX_INVERTERREADBOOL = 15
MAX_INVERTERBOOL = 31  # write + read
MAX_INVERTERWRITEINT = 15
MAX_INVERTERREADINT = 15
MAX_INVERTERINT = 31  # write + read
ACKBOOL_PROG = 0
ACKBOOL_TABSTAT = 1
ACKBOOL_TABSTAT2 = 2
ACKBOOL_CONFIGSAVE = 4
ACKBOOL_JOB = 3  # era ACKBOOL_SETTINGS
MAX_ACKBOOL = 6
ACKBOOL_SLIDER = 5
ACKBOOL_INSTTIME = 6
ALARM_BOOL_CONFIG = 0
ALARM_BOOL_FLAGOUT = 1
ALARM_INT_MODE = 0
ALARM_INT_INDIN = 1
ALARM_INT_INDOUT = 2
ALARM_INT_COD = 3
MAX_ALARMBOOL = 1
MAX_ALARMINT = 9  # era 5 in v.22
MAX_ALARM = 223  # da v.25.45, erano 191 da v.0.24
MAX_STOP = 31
MAX_WARNING = 111  # da v.25.45, erano 95 da v.0.24
ALARM_INT_INDENAB = 4
ALARM_INT_INDDISAB = 5
ALARM_COD_LC1_RESETREQ = 517
ALARM_COD_LC2_RESETREQ = 518
ALARM_COD_LC3 = 519
ALARM_COD_GATE2 = 520
ALARM_COD_GATE1_RESETREQ = 521
ALARM_COD_SAFETYMODERR = 522
ALARM_COD_GATE2_RESETREQ = 523
ALARM_COD_LC3_RESETREQ = 524
ALARM_COD_PB1 = 525  # ALARM_COD_ESTOP_MAIN
ALARM_COD_ES1 = 526  # ALARM_COD_ESTOP_MACHINE
ALARM_COD_LC1 = 527
ALARM_COD_LC2 = 528
ALARM_COD_GATE1 = 529
ALARM_COD_KE12 = 530
ALARM_COD_KE34 = 531
ALARM_COD_TWOHANDS = 532
ALARM_COD_PB2 = 533
ALARM_COD_PB3 = 534
ALARM_COD_PB4 = 535
ALARM_COD_PB5 = 536
ALARM_COD_PB6 = 537
ALARM_COD_PB7 = 538
ALARM_COD_PB8 = 539
ALARM_COD_ES2 = 540
ALARM_COD_ES3 = 541
ALARM_COD_LC4 = 542
ALARM_COD_LC4_RESETREQ = 543
ALARM_COD_LC5 = 544
ALARM_COD_LC5_RESETREQ = 545
ALARM_COD_LS1 = 546
ALARM_COD_LS1_RESETREQ = 547
ALARM_COD_LS2 = 548
ALARM_COD_LS2_RESETREQ = 549
ALARM_COD_LS3 = 550
ALARM_COD_LS3_RESETREQ = 551
ALARM_COD_LS4 = 552
ALARM_COD_LS4_RESETREQ = 553
ALARM_COD_GATE3 = 554
ALARM_COD_GATE3_RESETREQ = 555
ALARM_COD_GATE4 = 556
ALARM_COD_GATE4_RESETREQ = 557
ALARM_COD_GATE5 = 558
ALARM_COD_GATE5_RESETREQ = 559
ALARM_COD_SS3A = 560
ALARM_COD_SS4A = 561
ALARM_COD_SS5A = 562
ALARM_COD_SS6A = 563
ALARM_COD_RP1 = 564
ALARM_COD_SS1A = 515
ALARM_COD_SS2A = 516
ALARM_COD_FIRSTWARNING = 500  # Tutti i Warning possono essere Safety
ALARM_INT_INDREQACK = 6
ALARM_INT_INDACK = 7
ALARM_INT_TIMEOUT = 8
ALARM_INT_FREE_9 = 9
ALARM_COD_SS1B = 589
ALARM_COD_SS2B = 590
ALARM_COD_SS3B = 591
ALARM_COD_SS4B = 592
ALARM_COD_SS5B = 593
ALARM_COD_SS6B = 594
ALIGN_INIT = 1  # Stato di partenza
ALIGN_CENTSTART = 2
ALIGN_CENTOK = 3
ALIGN_OK = 8
ALIGN_ERROR = -1
ALIGN_CENTOPENA = 4
ALIGN_END = 9
ALIGN_ALIGN = 7
ALIGN_CENTOPENB = 5
ALIGN_CENTOPENAB = 6
ALIGN_A = 1
ALIGN_B = 2
ALIGN_NONE = 0
ALIGN_SWITCH = 10
ALIGN_INITOK = 11
ALIGN_SASDOWN = 12
ALIGN_SASUP = 13
ALIGN_OPENALL = 14
MAX_ALIGNINTPARAM = 11
MAX_ALIGNREALPARAM = 19
ALIGN_MAXCENTIND = 1
ALIGN_MAXCENT = 9
ALIGN_PRECENT = 16
ALIGN_INFEED = 15
ALIGN_CENTTYPE_1 = 0  # prima centratura - un passo
ALIGN_CENTTYPE_2A = 1  # prima centratura - due passi - 6436
ALIGN_CENTTYPE_2B = 2  # prima centratura - due passi - 6498
ALIGN_SASINIT = 17
ALIGN_TABLELIFTUP = 18
ALIGN_TABLELIFTDOWN = 19
ALIGN_CENTTYPE_1A = 3  # centratura unica con pressostato psa - 6761
ALIGN_CENTPSONLY = 20  # centraggio solo con un ps - 6761
ALIGN_CENTTYPE_NONE = -1  # nessuna centratura
ALIGN_CENTTYPE_1B = 4  # centratura un passo in posizione e psa - 6760
FUN_AXIS_UNLOADER = 9  # Scarico DE - era FUN_AXIS_BAL
FUN_AXIS_BEND = 1
FUN_AXIS_BENDLIFT = 20
FUN_AXIS_BENDMICRO = 11
FUN_AXIS_BENDSIDESUPP = 7
FUN_AXIS_BENDSLIDE = 18
FUN_AXIS_BENDTURN = 22
FUN_AXIS_CON = 15
FUN_AXIS_DE = 8
FUN_AXIS_EJ = 12
FUN_AXIS_EXT = 13
FUN_AXIS_FLOAT = 14
FUN_AXIS_HORSUPP = 29
FUN_AXIS_LR = 5
FUN_AXIS_OILTEMP = 23
FUN_AXIS_PINCH = 3
FUN_AXIS_PP1 = 27
FUN_AXIS_PP2 = 28
FUN_AXIS_PRE = 0
FUN_AXIS_PRELIFT = 19
FUN_AXIS_PREMICRO = 10
FUN_AXIS_PRESIDESUPP = 6
FUN_AXIS_PRESLIDE = 17
FUN_AXIS_PRETURN = 21
FUN_AXIS_PUSH = 16
FUN_AXIS_ROT = 2
FUN_AXIS_SP1 = 24
FUN_AXIS_SP2 = 25
FUN_AXIS_SP3 = 26
FUN_AXIS_SR = 4
FUN_AXIS_TILT = 30
MAX_ASSEFUNIND = 71  # era 54 prima di modifiche 6436
FUN_AXIS_STARTSENSOR = 31
FUN_AXIS_PRESIDESUPP2 = 32
FUN_AXIS_BENDSIDESUPP2 = 33
FUN_AXIS_PRESIDESUPP3 = 34
FUN_AXIS_BENDSIDESUPP3 = 35
FUN_AXIS_SPIRDEV = 36
FUN_AXIS_EB = 37
FUN_AXIS_ALIGNSASA = 38  # Posizione tastatore lato A
FUN_AXIS_ALIGNSASB = 39  # Posizione tastatore lato B
FUN_AXIS_ALIGNCENTA0 = 40  # Centratore supporto laterale lato A (Align)
FUN_AXIS_ALIGNCENTB0 = 41  # Centratore supporto laterale lato B (Align)
FUN_AXIS_ALIGNCENTA1 = 42  # Centratore rulliera
FUN_AXIS_ALIGNCENTB1 = 43  # Centratore rulliera
FUN_AXIS_ALIGNCENTA2 = 44  # Centratore rulliera
FUN_AXIS_ALIGNCENTB2 = 45  # Centratore rulliera
FUN_AXIS_ALIGNCENTA3 = 46  # Centratore rulliera
FUN_AXIS_ALIGNCENTB3 = 47  # Centratore rulliera
FUN_AXIS_ALIGNCENTA4 = 48  # Centratore rulliera - opzionale
FUN_AXIS_ALIGNCENTB4 = 49  # Centratore rulliera - opzionale
FUN_AXIS_ALIGNROLLTABROT = 50  # Rotazione rulliera
FUN_AXIS_ALIGNROLLTABTILT = 51  # Tilting rulliera
FUN_AXIS_ALIGNSASUPDOWN = 52  # Movimento tastatori - opzionale
FUN_AXIS_RELBLOCK = 53
FUN_AXIS_PRELOAD = 54
FUN_AXIS_PRESFC = 58  # Prebend Support Front Clamp
FUN_AXIS_PRESRC = 59  # Prebend Support Rear Clamp
FUN_AXIS_BENDSFC = 60  # Bend Support Front Clamp
FUN_AXIS_BENDSRC = 61  # Bend Support Rear Clamp
FUN_AXIS_MLFC = 62  # era FUN_AXIS_PREMFC
FUN_AXIS_MLRC = 63  # era FUN_AXIS_PREMRC
FUN_AXIS_MRFC = 64  # era FUN_AXIS_BENDMFC
FUN_AXIS_MRRC = 65  # era FUN_AXIS_BENDMRC
FUN_AXIS_TAL = 66  # Table A Lift
FUN_AXIS_TBL = 67  # Table B Lift
FUN_AXIS_RTTEMP = 68  # RT Oil Temp
FUN_AXIS_FREE_69 = 69
FUN_AXIS_PRELOAD2 = 55
FUN_AXIS_PRELOAD3 = 56
FUN_AXIS_PRELOAD4 = 57
FUN_AXIS_FREE_70 = 70
FUN_AXIS_FREE_71 = 71
ASSE_BOOL_BP1 = 1
ASSE_BOOL_BP2 = 2
ASSE_BOOL_BP3 = 3
ASSE_BOOL_BP4 = 4
ASSE_BOOL_BP5 = 5
ASSE_BOOL_BP6 = 6
ASSE_BOOL_DISABLEDELTA = 30  # era ASSE_BOOL_SYSPRESS1
ASSE_BOOL_ENABSH0 = 31  # era ASSE_BOOL_SYSPRESS2
ASSE_BOOL_ENABSL0 = 32  # era ASSE_BOOL_SYSPRESS3
ASSE_BOOL_FLAGCOUPMAX = 13  # era ASSE_BOOL_PINCH
ASSE_BOOL_SHOWMAN = 14
ASSE_BOOL_SHOWAUTO = 15
ASSE_BOOL_ENABAXIS = 16
ASSE_BOOL_ENABINTERP = 17
ASSE_BOOL_ENABTEACH = 18
ASSE_BOOL_ENABSMAX = 19
ASSE_BOOL_ENABSMIN = 20
ASSE_BOOL_ENABSHH = 21
ASSE_BOOL_ENABSH = 22
ASSE_BOOL_ENABSL = 23
ASSE_BOOL_ENABSLL = 24
ASSE_BOOL_CONFIGUP = 25
ASSE_BOOL_CONFIGDOWN = 26
ASSE_BOOL_FLAGINV = 27
ASSE_BOOL_CONFIG = 0
ASSE_BOOL_SHOWDELTA = 29
MAX_ASSEBOOL = 40
ASSE_BOOL_CHECKSTOPDISABLED = 28
ASSE_BOOL_MANSPUP = 33
ASSE_BOOL_MANSPDOWN = 34
ASSE_BOOL_SHOWDELTATAB = 35
ASSE_BOOL_NOMACHINESTARTED = 36  # era ASSE_BOOL_PIDENABLE
ASSE_BOOL_BP7 = 7
ASSE_BOOL_BP8 = 8
ASSE_BOOL_BP9 = 9
ASSE_BOOL_BP10 = 10
ASSE_BOOL_BP11 = 11
ASSE_BOOL_BP12 = 12
ASSE_BOOL_AXISNOMOVE = 37
ASSE_BOOL_COUPCALC = 38  # flag calcolo quota asse accoppiato (master)
ASSE_BOOL_FREE_39 = 39
ASSE_BOOL_FREE_40 = 40
ASSE_INT_ALTFB = 30
ASSE_INT_ALTFBDIG = 31
ASSE_INT_BOOSTVAL = 25
ASSE_INT_DEFSPEED = 27
ASSE_INT_INPUT2 = 3
ASSE_INT_INPUT4 = 5
ASSE_INT_FEEDBACK = 1
ASSE_INT_OUTPUT4 = 9  # era ASSE_INT_GRAFIND
ASSE_INT_INDSH = 33
ASSE_INT_INDSHH = 32
ASSE_INT_INDSL = 34
ASSE_INT_INDSLL = 35
ASSE_INT_INFLSIND = 20
ASSE_INT_INPUT = 2
ASSE_INT_INPUT3 = 4
ASSE_INT_INTERPGROUP = 29
ASSE_INT_LABELCOL = 12
ASSE_INT_LABELCOLIMP = 16
ASSE_INT_LABELNDEC = 14
ASSE_INT_LABELNDECIMP = 18
ASSE_INT_LABELNTOT = 13
ASSE_INT_LABELNTOTIMP = 17
ASSE_INT_LABELROW = 11
ASSE_INT_LABELROWIMP = 15
ASSE_INT_MASTER = 0
ASSE_INT_MOVEMODE = 28
ASSE_INT_OUTPUT1 = 6
ASSE_INT_P1 = 21
ASSE_INT_P2 = 22
ASSE_INT_OUTPUT2 = 7  # era ASSE_INT_PID
ASSE_INT_LABELTYPE = 10  # era ASSE_INT_SEQID
ASSE_INT_SUPLSIND = 19
ASSE_INT_TIMEOUT1 = 23  # PIDTimeout Auto
ASSE_INT_TIMEOUT2 = 24  # PIDTimeout Man - sostituisce PIDMULT
ASSE_INT_OUTPUT3 = 8  # era ASSE_INT_TIPO
ASSE_INT_TIPOMISURA = 26
ASSE_INT_SAFETYUPIND1 = 36
ASSE_INT_SAFETYUPIND2 = 37
ASSE_INT_SAFETYUPIND3 = 38
ASSE_INT_SAFETYDOWNIND1 = 48
ASSE_INT_SAFETYDOWNIND2 = 49
ASSE_INT_SAFETYDOWNIND3 = 50
ASSE_INT_INDSH0 = 42
ASSE_INT_INDSL0 = 43
ASSE_INT_INDMEM = 44
MAX_ASSEINT = 94  # era 90 in v.0.18
ASSE_INT_PERACQ = 45  # Periodo ciclo di acquisizione in msec
ASSE_INT_NUMTIMEOUT = 46  # Numero cicli per allineamento slave
ASSE_INT_PERVELAVG = 47  # Periodo velocità media HMI in msec
ASSE_INT_SAFETYUPIND4 = 39
ASSE_INT_SAFETYUPIND5 = 40
ASSE_INT_SAFETYUPIND6 = 41
ASSE_INT_SAFETYDOWNIND4 = 51
ASSE_INT_SAFETYDOWNIND5 = 52
ASSE_INT_SAFETYDOWNIND6 = 53
NUM_ASSE_SAF = 6
ASSE_INT_DELAYUP = 54
ASSE_INT_DELAYDOWN = 55
ASSE_INT_MAXVELPERC = 56
ASSE_INT_DECOUPMASTER = 57
ASSE_INT_DECOUPMASTER2 = 58
ASSE_INT_DECOUPMASTER3 = 59
ASSE_INT_DECOUPMASTER4 = 60
ASSE_INT_DECOUPMASTER5 = 61
ASSE_INT_DECOUPMASTER6 = 62
NUM_ASSE_INPUT = 4
NUM_ASSE_DECOUP = 6
ASSE_INT_PS = 63
ASSE_INT_BWVSLOW = 64
ASSE_INT_FWVSLOW = 65
ASSE_INT_PS2 = 66
ASSE_INT_PS3 = 67
ASSE_INT_AXISCOUPCHECK = 68
ASSE_INT_TEACHMINMULT = 69
ASSE_INT_BWVSLOW2 = 71  # era ASSE_INT_SLOWIND - DISABLED HDMC
ASSE_INT_FWVSLOW2 = 70  # era ASSE_INT_FASTIND
ASSE_INT_PID = 72  # era 7
ASSE_INT_GRAFIND = 73  # era 9
ASSE_INT_DELTA1 = 74
ASSE_INT_OPTPARAMIND = 75  # era ASSE_INT_DELTA2 - NON USATO
ASSE_INT_DISABLEBP1 = 76
ASSE_INT_DISABLEBP2 = 77
ASSE_INT_DISABLEBP3 = 78
ASSE_INT_DISABLEBP4 = 79
NUM_ASSE_OUTPUT = 4
ASSE_INT_DISABLEBP5 = 80
ASSE_INT_DISABLEBP6 = 81
ASSE_INT_DISABLEBP7 = 82
ASSE_INT_DISABLEBP8 = 83
ASSE_INT_DISABLEBP9 = 84
ASSE_INT_DISABLEBP10 = 85
ASSE_INT_DISABLEBP11 = 86
ASSE_INT_DISABLEBP12 = 87
ASSE_INT_OPTPARAM1IND = 88  # era ASSE_INT_MOVINGIND
ASSE_INT_OPTPARAM2IND = 89  # era ASSE_INT_UPIND
ASSE_INT_OPTPARAM3IND = 90  # era ASSE_INT_DOWNIND
ASSE_HOLDTORUNTYPE_NONE = 0
ASSE_HOLDTORUNTYPE_ROLL = 1
ASSE_HOLDTORUNTYPE_OTHER = 2
ASSE_HOLDTORUNTYPE_ANY = 3
ASSE_INT_HOLDTORUNTYPE = 91
ASSE_INT_RCOUTUPIND = 92
ASSE_INT_RCOUTDOWNIND = 93
ASSE_INT_RCOUTMOVINGIND = 94
ASSE_REAL_BWVMAX = 14  # typ=6 se lung (? se press)
ASSE_REAL_COEFFDOWN = 3  # typ=-1
ASSE_REAL_COEFFUP = 2  # typ=-1
ASSE_REAL_DSMAXDOWN = 15  # typ=axtyp
ASSE_REAL_DSMAXUP = 16  # typ=axtyp
ASSE_REAL_FWVMAX = 17  # typ=6 (? se press)
ASSE_REAL_P1DOWN = 5  # typ=1
ASSE_REAL_P1UP = 4  # typ=1
ASSE_REAL_P2DOWN = 7  # typ=1
ASSE_REAL_P2UP = 6  # typ=1
ASSE_REAL_SH = 24  # typ=axtyp
ASSE_REAL_SHH = 23  # typ=axtyp
ASSE_REAL_SINF = 21  # typ=axtyp
ASSE_REAL_SL = 25  # typ=axtyp
ASSE_REAL_SLL = 26  # typ=axtyp
ASSE_REAL_SMAX = 18  # typ=axtyp
ASSE_REAL_SMIN = 19  # typ=axtyp
ASSE_REAL_SRTDOWN = 1  # typ=-1 (tempo)
ASSE_REAL_SRTUP = 0  # typ=-1 (tempo)
ASSE_REAL_SSUP = 20  # typ=axtyp
ASSE_REAL_SYSPRESSDOWN1 = 9  # typ=1
ASSE_REAL_SYSPRESSDOWN2 = 11  # typ=1
ASSE_REAL_SYSPRESSDOWN3 = 13  # typ=1
ASSE_REAL_SYSPRESSUP1 = 8  # typ=1
ASSE_REAL_SYSPRESSUP2 = 10  # typ=1
ASSE_REAL_SYSPRESSUP3 = 12  # typ=1
ASSE_REAL_TILTMAX = 27  # typ=axtyp
ASSE_REAL_VMINSTARTED = 22  # typ=6 (? se press)
MAX_ASSEREAL = 54
ASSE_REAL_SLAVEVRESET = 31  # 20
ASSE_REAL_SLAVEVMIN = 32  # 10
ASSE_REAL_MASTERMULT = 28  # 1.7
ASSE_REAL_MASTERDELTAMIN = 29  # 2.0 mm
ASSE_REAL_MASTERKSRS = 30  # 1.2
ASSE_REAL_SLAVEDELTATSTART = 33  # 500
ASSE_REAL_OUTKP = 34  # 0.1
ASSE_REAL_OUTDELTAT = 35  # 500
ASSE_REAL_SH0 = 36
ASSE_REAL_SL0 = 37
ASSE_REAL_TILTMAXDOWN = 38
ASSE_REAL_FREE_39 = 39  # era ASSE_REAL_TILTMAXTEACH
ASSE_REAL_DELTAMOVINGUP = 40
ASSE_REAL_DELTAMOVINGDOWN = 41
ASSE_REAL_DELTADIV = 42
ASSE_REAL_DELTAMOVINGSUPUP = 43
ASSE_REAL_DELTAMOVINGINFUP = 44
ASSE_REAL_DELTAMOVINGSUPDOWN = 45
ASSE_REAL_DELTAMOVINGINFDOWN = 46
ASSE_REAL_DELTAAUTO = 47
ASSE_REAL_BWACCMAX = 48
ASSE_REAL_FWACCMAX = 49
ASSE_REAL_OPTPARAM1 = 50
ASSE_REAL_OPTPARAM2 = 51
ASSE_REAL_OPTPARAM3 = 52
ASSE_REAL_AXISCOUPMIN = 53
ASSE_REAL_FREE_54 = 54
CMDBOOL_QUALITY_ACK = 0
CMDBOOL_QUALITY_END = 1
CMDBOOL_QUALITY_GOOD = 2
CMDBOOL_TELESERVICE_ACK = 3
CMDBOOL_TELESERVICE_AUTH = 4
CMDINT_TELESERVICE_STATUS = 2
CMDREAL_MANOFFSETPINCHPRESS = 0  # era CMDREAL_CURRPROG_PINCHPRESS
CMDBOOL_SLIDER_ACK = 5  # era CMDBOOL_SIM_REQ
STRING_MODEL = 0  # PARAM
CMDBOOL_EYEBEND_REQ = 6
CMDDINT_EYEBEND_COMMAND = 0
MAX_CMDBOOL = 32  # era 27
MAX_CMDDINT = 1
MAX_CMDINT = 12  # era 10 - aggiunto CMDINT_JOBLASTOP - aggiunto CMDINT_CURRIND
MAX_CMDREAL = 5  # era 3 prima di APPLYRESET, era 1 prima di 6498
CMDBOOL_DEBUG_DISABLEFB = 7  # era CMDBOOL_DISABLE_FB
CMDBOOL_CONFIG_REQ = 8
CMDBOOL_CONFIG_ACK = 9
CMDBOOL_PROG_REQ = 11  # era CMDBOOL_PROG_REQHMI
CMDBOOL_CONFIG_SAVEREQ = 10
CMDBOOL_GREASE_TEST = 12
CMDBOOL_GREASE_PUMP = 13
CMDBOOL_GREASE_RESET = 14
CMDINT_DEBUGHMI = 0  # CMD_UM, CMD_FREE0
CMDINT_SINGMOV_VALUE = 1
CMDBOOL_SINGMOV_STAT = 15
CMDBOOL_CONFIG_REQHMI = 16
CMDINT_TABCOMM_CMD = 3
CMDINT_TABCOMM_SET = 4
CMDINT_CURRPOSHMI = 5
CMDBOOL_AUTOCORR = 17
CMDINT_FREE_6 = 6  # era CMDINT_TABSTATFIRST
CMDINT_CURRDIAGIND = 7
TABSTAT_FIRST = 4  # prima colonna variabile (fisse: Rot,L,R;P, Speed non è indicizzata)
CMDBOOL_TABSTAT_REQ = 18
CMDBOOL_APPLYROT_END = 19  # era CMDBOOL_TABSTAT_ACK
CMDREAL_AUTOPROGLENGTH = 1
CMDBOOL_REPEATEND_END = 20  # era CMDBOOL_SETTINGS_REQ
CMDBOOL_APPLYRESET_END = 21  # era CMDBOOL_SETTINGS_ACK
CMDBOOL_FREE_22 = 22  # era CMDBOOL_PROG_ACK
CMDBOOL_FREE_23 = 23  # era CMDBOOL_SIM_ACK
CMDBOOL_TABSTAT2_REQ = 24
CMDBOOL_INSTTIME_SET = 25  # era CMDBOOL_TABSTAT2_ACK
CMDBOOL_APPLY_END = 26
CMDBOOL_APPLY_OK = 27
CMDBOOL_DEBUG_DISABLEOUT = 28
CMDBOOL_DEBUG_ENABLEOUT = 29
CMDBOOL_DEBUG_MAINTSIM = 30
CMDBOOL_DEBUG_DISABLEPRESS = 31
CMDREAL_AUTOPROGWIDTH = 2
CMDREAL_AUTOPROGTHICKNESS = 3
CMDBOOL_SYNDIAGON = 32
CMDINT_CURRDIAGIND2 = 8
CMDINT_CURRDIAGIND3 = 9
CMDINT_CURRDIAGIND4 = 10
CMDINT_JOBLASTOP = 11
CMDREAL_APPLYRESETROT = 4
CMDREAL_FREE_5 = 5
FB_INT_TIPO = 0
FB_INT_TIPOMISURA = 1
FB_INT_RESETIND = 2  # era FB_INT_GATEIND
FB_INT_ININD = 3
FB_INT_OPT = 4  # era FB_INT_ERRIND
FB_REAL_DEADBAND = 0
FB_REAL_RATIO = 1
FB_REAL_SCALESUP = 2
FB_REAL_SCALEINF = 3
MAX_FEEDBACK = 47
MAX_FEEDBACKINT = 4
MAX_FEEDBACKREAL = 3
MAX_FEEDBACKDINT = 1  # v.21
FB_DINT_INF = 0
FB_DINT_SUP = 1
FB_OPT_NONE = -1
FB_OPT_LEFT = 0
FB_OPT_RIGHT = 1
IO_SYSTYPE_SYSTEMBOOL = 10
IO_SYSBOOL_PARAM = 1
IO_SYSBOOL_STATUS = 0
IO_SYSTYPE_SYSTEMREAL = 13
IO_SYSTYPE_AXISREAL = 15
IO_SYSREAL_SYSTEM = 0
IO_SYSAXISREAL_POS = 0
IO_SYSAXISREAL_SPEED = 1
IO_SYSAXISREAL_DELTA = 2
IO_SYSAXISREAL_SUP = 3
IO_SYSAXISREAL_MAX = 4
IO_SYSAXISREAL_HH = 5
IO_SYSAXISREAL_H = 6
IO_SYSAXISREAL_L = 7
IO_SYSAXISREAL_LL = 8
IO_SYSAXISREAL_MIN = 9
IO_SYSAXISREAL_INF = 10
IO_SYSAXISREAL_H0 = 11
IO_SYSAXISREAL_L0 = 12
IO_SYSAXISREAL_TILTMAXUP = 13
IO_SYSAXISREAL_TILTMAXDOWN = 14
IO_SYSREALSTAT_TIMEINSTALL = 0
IO_SYSREALSTAT_TIMEPOWERON = 1
IO_SYSREALSTAT_TIMEPOWEROFF = 2
IO_SYSTYPE_FEEDBACKREAL = 14
IO_SYSFBREAL_VAL = 0
IO_SYSFBREAL_RATIO = 1
IO_SYSFBREAL_DEADBAND = 2
IO_SYSFBREAL_SCALESUP = 3
IO_SYSFBREAL_SCALEINF = 4
IO_SYSREAL_STAT = 1
IO_SYSREALSTAT_TIMERUN = 3
IO_SYSREALSTAT_TIMERUNAUTO = 4
IO_SYSREALSTAT_TIMERUNMAN = 5
IO_SYSREALSTAT_TIMEFAIL = 6
IO_SYSREALSTAT_TIMEEFF = 7
IO_SYSREALSTAT_TIMEEFFAUTO = 8
IO_SYSREALSTAT_TIMEEFFMAN = 9
IO_SYSREALSTAT_TIMESETUP = 10
IO_SYSREALSTAT_TIMESTANDBY = 11
MAX_JOB = 99
MAX_JOBTAB = 13
JOBBOOL_TOP = 0
JOBBOOL_PGUP = 1
JOBBOOL_UP = 2
JOBBOOL_DOWN = 3
JOBBOOL_PGDOWN = 4
JOBBOOL_BOTTOM = 5
JOBBOOL_FILTER = 7
JOBBOOL_OPEN = 8
JOBBOOL_CLOSE = 9
MAX_JOBBOOL = 14
JOBBOOL_SEL = 6
JOBBOOL_GOOD = 10
JOBBOOL_BAD = 11
JOBBOOL_INIT = 12
JOBBOOL_OK = 13
JOBBOOL_CANCEL = 14
JOB_OP_OPEN = 1
JOB_OP_GOOD = 2
JOB_OP_BAD = 3
JOB_OP_CLOSE = 4
JOBINT_FREE_0 = 0  # era JOBINT_LASTOP
JOBINT_NTOT = 1
JOBINT_NGOOD = 2
JOBINT_TCICLO = 3
JOBINT_TOTPEZZI = 4
MAX_JOBINT = 5
JOB_OP_LOAD = 5
JOB_OP_TERM = 6
JOB_OP_MANBEGIN = 7
JOB_OP_MANEND = 8
JOBINT_OPENED = 5
JOB_OP_NONE = -1
JOB_OP_BEGIN = 9
JOB_OP_ERR = 0  # non usato
JOBS_NONE = 0
JOBS_CSV = 1
JOBS_OPCUA1 = 2  # 6703
JOB_OP_REQ = 10
JOBS_OPCUA2 = 3  # altre implementazioni future
JOBS_OPCUA3 = 4  # ...
BOOL_INVERTER = 0  # era BOOL_RADIOCONTROL
BOOL_STEP = 1
BOOL_TOOLSET = 2
BOOL_MATERIAL = 3
BOOL_DEAUTO = 4
BOOL_ROUNDOLOGO = 5  # era BOOL_SHOWROLLSSPEED - era BOOL_STARTSENSOR
BOOL_DEFPROGTYPE = 9
BOOL_EBEXT = 10  # era BOOL_EB
BOOL_EBNODIST = 11  # era BOOL_JOBS
BOOL_QUALITY = 12
BOOL_COUNTER = 13
BOOL_DRAWINGMAND = 14
BOOL_DXFENABLE = 15
BOOL_DXFPDEC = 16
BOOL_UMPRESS = 17
BOOL_UMYP = 18
BOOL_UMTEMP = 19
BOOL_PASSPINCHPOT = 20
BOOL_PASSPINCHPOT2 = 21
BOOL_PASSPINCHTILT = 22
BOOL_PASSPINCHBAR = 23
BOOL_PASSPINCHIN = 24
BOOL_SHOWDEMAN = 25  # era BOOL_PASSWORK
BOOL_PASSPINCH2STEPS = 26
BOOL_RORIENT = 27
BOOL_RGUIDESPEEDPOT = 28
BOOL_RGUIDESPEEDBAR = 29
BOOL_RGUIDESPEEDIN = 30
BOOL_SHOWDELTA = 31
BOOL_TELESERVICE = 32
BOOL_TUNING = 33
BOOL_ZEROTOP = 34
BOOL_NL = 35
BOOL_HMITYPE = 8  # True -> WCNC4 Roundo - False-> PGS-X Faccin
BOOL_FEEDSIDE = 7
BOOL_AUTO = 6  # Se TRUE -> gestione fotocellule e/o laser scanner
BOOL_USER = 36  # era BOOL_SIMGRAPH
BOOL_INTERPCALCTYPE = 37  # era BOOL_SIMCALC
BOOL_AUTOCORR = 38
BOOL_ALIGNENABLE = 39
BOOL_BWPREBENDENABLE = 40  # era BOOL_WTENABLE
BOOL_LOADER = 41
BOOL_WT = 42
BOOL_ALIGNSASSELECT = 43  # Possibilità di selezione SAS o SAS2
BOOL_CURRFEEDSIDE = 44
BOOL_CURRORIENT = 45
BOOL_CAPACITYMSG = 46
BOOL_CAPACITYPAGE = 47
BOOL_SHAPEREBEND2 = 48
BOOL_DEFORIENT = 49  # 0 = Horiz, 1 = Vert
BOOL_SAFETYBPDISAB = 50  # era BOOL_ARCHIMETER
BOOL_PROGDESCR = 51  # era BOOL_ARCHIMETER_DEBUG
BOOL_RCSW = 52
BOOL_ENERGYMETER = 53
BOOL_CILDIFF = 54
BOOL_NOTILT = 55
BOOL_SINGLEPV = 56
BOOL_NEWCONSOLE = 57
BOOL_IMPORT = 58
BOOL_SYNDIAG = 59
BOOL_MACHINECLAMPS = 60
BOL_PREBENDCALCTYPE = 61
BOOL_FBROTLOWER = 62
BOOL_SYNCLOADAFTERPRELOAD = 64  # era BOOL_SYNCLOAD
BOOL_DATALOGGERIDFILE = 65  # era BOOL_SYNCUNLOAD
BOOL_FREE_66 = 66  # era BOOL_SYNCLOADDI
BOOL_FREE_67 = 67  # era BOOL_SYNCUNLOADDI
BOOL_FREE_68 = 68  # era BOOL_SYNCSTART
BOOL_FREE_69 = 69  # era BOOL_SYNCSTARTDI
BOOL_FREE_70 = 70
BOOL_FREE_71 = 71
BOOL_SMARTCLIENT = 63
MAX_PARAMBOOL = 71  # da 63 a 71 in v.0.25.42.1; da 59 a 63 in v.0.25.28
INT_BP4TIMEOUT = 17  # BP3
INT_BP1TIMEOUT = 14  # BP0
INT_BP2TIMEOUT = 15  # BP1
INT_BP3TIMEOUT = 16  # BP2
INT_REFTIME = 5
INT_HOLDTORUNTYPE = 6
INT_NUMCICLIAVG = 7
INT_DEFRADIUSTYPE = 8
INT_DECPTYPE = 9  # potrebbe essere bool
INT_SEPCHTYPE = 10
INT_PINCHTYPE = 11  # era INT_PASSPINCHTYPE
INT_MACHTYPE = 1
INT_CALCTYPE = 2
INT_SN = 0
INT_BP5TIMEOUT = 18  # BP4
INT_BP6TIMEOUT = 19  # BP5
MAX_PARAMINT = 79  # era 72 nella v.0.18
MAX_GREASEV = 16
INT_GREASEIN1 = 32
INT_GREASEIN10 = 41
INT_GREASEIN11 = 42
INT_GREASEIN12 = 43
INT_GREASEIN13 = 44
INT_GREASEIN14 = 45
INT_GREASEIN15 = 45
INT_GREASEIN16 = 47
INT_GREASEIN2 = 33
INT_GREASEIN3 = 34
INT_GREASEIN4 = 35
INT_GREASEIN5 = 36
INT_GREASEIN6 = 37
INT_GREASEIN7 = 38
INT_GREASEIN8 = 39
INT_GREASEIN9 = 40
INT_ROLLIND = 26  # era INT_GREASELEVEL
INT_GREASENUMFB = 30
INT_GREASENUMV = 64
INT_GREASEOUT1 = 48
INT_GREASEOUT10 = 57
INT_GREASEOUT11 = 58
INT_GREASEOUT12 = 59
INT_GREASEOUT13 = 60
INT_GREASEOUT14 = 61
INT_GREASEOUT15 = 62
INT_GREASEOUT16 = 63
INT_GREASEOUT2 = 49
INT_GREASEOUT3 = 50
INT_GREASEOUT4 = 51
INT_GREASEOUT5 = 52
INT_GREASEOUT6 = 53
INT_GREASEOUT7 = 54
INT_GREASEOUT8 = 55
INT_GREASEOUT9 = 56
INT_GREASEPUMPON = 65
INT_GREASEPUMPSTART = 27
INT_GREASETIMEOUT1 = 28
INT_GREASETIMEOUT2 = 29
INT_FREE_31 = 31  # era INT_GREASETR
INT_BP7TIMEOUT = 20
INT_BP8TIMEOUT = 21
INT_BP9TIMEOUT = 22
INT_BP10TIMEOUT = 23
INT_BP11TIMEOUT = 24
INT_BP12TIMEOUT = 25
INT_HOLDTORUNTIMEOUT = 12
INT_HOLDTORUNTIMEOUT2 = 13
INT_CHECKTYPE = 3
INT_JOBTYPE = 66  # era INT_RECYCVALVEIND; INT_ALIGN_CENTFASTSPEED
INT_DATALOGGERID = 67  # era INT_RECYCVALVETIMEOUT; INT_ALIGN_CENTSLOWSPEED
INT_PINCHPRESSSPEED = 68  # era INT_ALIGN_ROTFASTSPEED
INT_FREE_70 = 70  # era INT_AVGDT_IND
INT_FREE_71 = 71  # era INT_NHDT_IND
INT_RESETTYPE = 72  # era INT_ALIGN_NUMCENT
INT_PRESSPINCHTYPE = 4
INT_RTTYPE = 69  # era INT_ALIGN_ROTSLOWSPEED
INT_ARCHIMETER_COMUSB = 73
INT_ARCHIMETER_COMWIFI = 74
INT_ARCHIMETER_TIMEOUT = 75
INT_RCTYPE = 76  # RadioControl Type
INT_RCSEL = 77  # RCSmall - selettore rullo
INT_ROLLERCHANGESEQ = 78
INT_ROLLNUM = 79
REAL_B0COEFF = 0  # typ=-1 NON USATO
REAL_LINTCOEFF = 1  # typ=-1
REAL_DEFINTFACT = 2  # typ=-1
REAL_DEFNL = 3  # typ=-1
REAL_MAXINTSPEED = 4  # typ=-1
REAL_TOPANG = 5  # typ=-1
REAL_STEPANG = 6  # typ=-1
REAL_STARTSENSX = 7  # typ=-1
REAL_STARTSENSZ = 8  # typ=-1
REAL_HADJUST = 10  # typ = 0
REAL_L0COEFF = 11  # era REAL_BWPRELINTCOEFF, era REAL_ADDITROT
REAL_B = 12  # typ = 0
REAL_H0 = 13  # typ = 0
REAL_LRDIAM = 14  # typ = 0
REAL_SRDIAM = 15  # typ = 0
REAL_TRDIAM = 16  # typ = 0
REAL_WIDTH = 17  # typ = 0
REAL_PINCHDELTATH = 18  # typ = 0
REAL_DAES = 19  # typ = 0
REAL_LROUTERDIAM = 20  # typ = 0
REAL_SROUTERDIAM = 21  # typ = 0
REAL_TROUTERDIAM = 22  # typ = 0
REAL_D = 23  # typ = 0
REAL_E = 24  # typ = 0
REAL_F = 25  # typ = 0
REAL_G = 26  # typ = 0
REAL_S = 27  # typ = 0
REAL_STARTSENSORDIST = 28  # typ = 0
REAL_BFSUPADJ = 29  # era REAL_RESETPINCHPOS, era REAL_TSDELTADOWN
REAL_BFINFADJ = 30  # era REAL_RESETBENDPOS, era REAL_TSDELTADOUP
REAL_K = 31  # era REAL_TSMINL
REAL_EXTDIST = 32  # typ = 0
REAL_LREFFCYLAREA = 33  # typ=8
REAL_DEFPINCHPRESS = 34  # typ=1
REAL_PINCHPRESSDELTA = 35  # typ=1
REAL_PINCHPRESSTEST = 36  # typ=1
MAX_PARAMREAL = 79  # era 62 nella v.0.18
REAL_LATSUPR0 = 37
REAL_LATSUPQ0 = 38
REAL_LATSUPR1 = 39
REAL_LATSUPQ1 = 40
REAL_LATSUPR2 = 41
REAL_LATSUPQ2 = 42
REAL_LATSUPR3 = 43
REAL_LATSUPQ3 = 44
REAL_LATSUPR4 = 45  # 0 o 999999 per attesa invito
REAL_LATSUPQ4 = 46  # quota attesa invito
REAL_B2ANG = 47
REAL_EYEBEND_BF = 48  # era REAL_MAXTILTTEACH
REAL_ALIGN_CENTDIST1 = 49
REAL_ALIGN_CENTDIST2 = 50
REAL_ALIGN_CENTDIST3 = 51
REAL_TSTY = 52  # era REAL_ALIGN_DELTAPOSOK - non usato
REAL_ALIGN_DELTACENTPOS = 53
REAL_EYEBEND_DX = 54  # distanza asse X con centro rullo superiore
REAL_EYEBEND_DZ = 55  # distanza asse Z con centro rullo superiore
REAL_EYEBEND_STEP = 56  # passo angolo
REAL_EYEBEND_XMAX = 57  # 360 -> -360 .. 360
REAL_EYEBEND_ZMIN = 58  # 580
REAL_EYEBEND_ZMAX = 59  # 1380
REAL_EYEBEND_DELTA = 60
REAL_ARCHIMETER_L1 = 61  # Spessore supporto centrale X
REAL_ARCHIMETER_L2 = 62  # Spessore supporto centrale Y
REAL_DELTAOFFSET = 9  # offset delta per assi in movimento
REAL_ARCHIMETER_L3 = 63
REAL_ARCHIMETER_A1 = 64
REAL_ARCHIMETER_B1 = 65
REAL_ARCHIMETER_C1 = 66
REAL_ARCHIMETER_A2 = 67
REAL_ARCHIMETER_B2 = 68
REAL_ARCHIMETER_C2 = 69
REAL_ARCHIMETER_A3 = 70
REAL_ARCHIMETER_B3 = 71
REAL_ARCHIMETER_C3 = 72
REAL_BFREBEND = 73
REAL_BFSTEP = 74
REAL_LSX = 75  # Distanza X centro - supporto laterale
REAL_LSY = 76  # Distanza Y centro - supporto laterale
REAL_LSL = 77  # Lunghezza supporto laterale
REAL_LST = 78  # Spessore supporto laterale
REAL_TSTX = 79
AXISMODE_ABS = 0
AXISMODE_REL = 1
AXSTAT_BAD = 14
AXSTAT_H = 2
AXSTAT_HH = 1
AXSTAT_INFLS = 7
AXSTAT_L = 5
AXSTAT_LL = 4
AXSTAT_MAX = 0
AXSTAT_MIN = 3
AXSTAT_P1DOWN = 9
AXSTAT_P1UP = 8
AXSTAT_P2DOWN = 11
AXSTAT_P2UP = 10
AXSTAT_SUPLS = 6
AXSTAT_TILT = 12
AXSTAT_SAF = 13
AXSTAT_H0 = 15
AXSTAT_L0 = 16
AXSTAT_SLOW = 17
AXSTAT_FAST = 18
BOOL_IND_AUTOMODESEL = 0
BOOL_IND_TEACHMODESEL = 1
BOOL_IND_CYCLEMODESEL = 2
BOOL_IND_STARTRESET = 3
BOOL_IND_TESTMODESEL = 23
BOOL_IND_REMOTEMODESEL = 4
BOOL_IND_EMGCYPB = 5  # Solo per segnale EMGCY proveniente da LEUZE MSI
BOOL_IND_CONSOLE2MODESEL = 6
BOOL_IND_INENABLED = 8  # era BOOL_IND_OILLEVEL
BOOL_IND_CHROLLMODESEL = 7
BOOL_IND_STARTIN = 12
BOOL_IND_STOPIN = 13
BOOL_IND_STARTEDIN = 14
BOOL_IND_HOLDTORUN = 15
BOOL_IND_RTCOUPLED = 16  # era CNCON - se serve gestito come allarme
BOOL_IND_LEFTSEL = 17  # era BOOL_IND_EMGCYPHOTOCELL
BOOL_IND_PINCHPRESS = 18  # era BOOL_IND_PROGACK
BOOL_IND_RIGHTSEL = 19  # era BOOL_IND_EMGCYPHOTOCELLRESETBTN
BOOL_IND_STARTSENSOR = 20  # usato ma commentato in Stat_Exec
BOOL_IND_MAINTRESET = 21
BOOL_IND_MANMODESEL = 22
BOOL_IND_SEMIAUTOMODESEL = 24
BOOL_IND_HOLDTORUN2 = 25
BOOL_IND_DISABLEBP1 = 26  # Disabilitazione generale BP
BOOL_IND_DISABLEBP2 = 27
BOOL_IND_DISABLEBP3 = 28
BOOL_IND_DISABLEBP4 = 29
BOOL_IND_DISABLEBP5 = 30
BOOL_IND_DISABLEBP6 = 31
BOOL_IND_DEBALNOTPRESS = 9  # Scritto da DropEnd, blocca i movimenti
BOOL_IND_CONSOLE1MODESEL = 10  # lasciato nel caso serva un segnale esplicito
BOOL_IND_SINGMOVSEL = 11
BOOL_IND_DISABLEBP7 = 32
BOOL_IND_DISABLEBP8 = 33
BOOL_IND_DISABLEBP9 = 34
BOOL_IND_DISABLEBP10 = 35
BOOL_IND_DISABLEBP11 = 36
BOOL_IND_DISABLEBP12 = 37
BOOL_IND_AUTOMODE = 38
BOOL_IND_AUTOCYCLEMODE = 39
BOOL_IND_AUTOSTEPMODE = 40
BOOL_IND_SEMIAUTOMODE = 41
BOOL_IND_TEACHMODE = 42
BOOL_IND_MANMODE = 43
BOOL_IND_CONSOLE1MODE = 44
BOOL_IND_CONSOLE2MODE = 45
BOOL_IND_REMOTEMODE = 46
BOOL_IND_CHROLLMODE = 47
BOOL_IND_SINGMOVMODE = 48
BOOL_IND_MACHINESTARTED = 49  # Usato per RUNTIME
BOOL_IND_OUTSWENAB = 50
BOOL_IND_GREASEPUMPON = 51
BOOL_IND_GREASEALARM = 52
BOOL_IND_GREASEPUMPALARM = 53
BOOL_IND_WAITINGFORSTART = 54
BOOL_IND_POWEROFFFLAG = 55
BOOL_IND_ALARMON = 56
BOOL_IND_STARTCMD = 57
BOOL_IND_ALARMSTOP = 58
BOOL_IND_MAINTON = 59
BOOL_IND_RTFWDISABLED = 60  # era BOOL_IND_MACHINELIGHT
BOOL_IND_LEFTMEM = 61  # era BOOL_IND_EMGCYPHOTOCELLRESET
BOOL_IND_RESETFLAG = 62
BOOL_IND_RIGHTMEM = 63  # era BOOL_IND_EMGCYPHOTOCELLLIGHT
BOOL_IND_OUTENABLED = 64
BOOL_IND_STOPCMD = 65
BOOL_IND_QUALITYENAB = 66
BOOL_IND_TELESERVICEREQ = 67
BOOL_IND_MICROMODESEL = 68  # usare per icona MICRO
BOOL_IND_APPLY = 69  # era BOOL_IND_SIMACK
BOOL_IND_QUALITYEND = 70
BOOL_IND_QUALITYGOOD = 72
BOOL_IND_PARTEND = 73  # era BOOL_IND_TCPCONNECTED
BOOL_IND_AUTOCORR = 74
BOOL_IND_PARTBEGIN = 75  # era BOOL_IND_EYEBENDRUN
BOOL_IND_AUTOCORRSTARTED = 76
BOOL_IND_TILTDISABLED = 77  # era BOOL_IND_FULLAUTODISABLED - era BOOL_IND_FAIL - usato ALARMSTOP
BOOL_IND_EYEBENDON = 78  # era BOOL_IND_MOVING
BOOL_IND_BP1 = 79
BOOL_IND_BP2 = 80
BOOL_IND_BP3 = 81
BOOL_IND_BP4 = 82
BOOL_IND_BP5 = 83
BOOL_IND_BP6 = 84
BOOL_IND_BP7 = 85
BOOL_IND_BP8 = 86
BOOL_IND_BP9 = 87
BOOL_IND_BP10 = 88
BOOL_IND_BP11 = 89
BOOL_IND_BP12 = 90
BOOL_IND_RCV0 = 91  # era BOOL_IND_EMGCYTOTPB
BOOL_IND_RCV1 = 92  # era BOOL_IND_EMGCYTOTPHOTOCELL
BOOL_IND_RCV2 = 93
BOOL_IND_RCV3 = 94  # era BOOL_IND_EMGCYPBFRONT
BOOL_IND_RCV4 = 95  # era BOOL_IND_EMGCYPBREAR
BOOL_IND_RCUM = 96  # era BOOL_IND_EMGCYPBFENCE
BOOL_IND_FREE_97 = 97  # era BOOL_IND_RCLUP, BOOL_IND_EMGCYPBFENCE2
BOOL_IND_FREE_98 = 98  # era BOOL_IND_RCLDOWN, BOOL_IND_EMGCYPHOTOCELL2
BOOL_IND_FREE_99 = 99  # era BOOL_IND_RCRUP, BOOL_IND_EMGCYPHOTOCELL3
BOOL_IND_FREE_100 = 100  # era BOOL_IND_RCRDOWN, BOOL_IND_EMGCYPHOTOCELL4
BOOL_IND_FREE_101 = 101  # era BOOL_IND_RCBUP, BOOL_IND_EMGCYDOOR
BOOL_IND_FREE_102 = 102  # era BOOL_IND_RCBDOWN, BOOL_IND_EMGCYDOOR2
BOOL_IND_FREE_103 = 103  # era BOOL_IND_RCTLEFT, BOOL_IND_EMGCYLASER
BOOL_IND_FREE_104 = 104  # era BOOL_IND_RCTRIGHT, BOOL_IND_EMGCYLIGHT
BOOL_IND_EMGCYRESETBTN = 105
BOOL_IND_RCALARM = 106  # era BOOL_IND_EMGCYDOORRESETBTN
BOOL_IND_EMGCYRESET = 107
BOOL_IND_INVERTERRESET = 108  # era BOOL_IND_EMGCYDOORRESET
BOOL_IND_INVERTERALARM = 109  # era BOOL_IND_EMGCYPHOTOCELLLIGHT2
BOOL_IND_PINCHPRESSFRONTREAR = 111
BOOL_IND_PINCHPRESSFRONTREAR2 = 112
BOOL_IND_HOLDTORUNRC = 113  # era BOOL_IND_SYNDIAGON
BOOL_IND_PRELOADUP = 114
BOOL_IND_PRELOADPINCHDISABLED = 115
BOOL_IND_PARTMAN = 116
BOOL_IND_PARTMANBEGIN = 117
BOOL_IND_PARTMANEND = 118
BOOL_IND_PARTMANRUNNING = 119
BOOL_IND_UNBALLEFT = 120  # era BOOL_IND_EMGCYPHOTOCELLREQ
BOOL_IND_UNBALRIGHT = 121  # era BOOL_IND_EMGCYPHOTOCELLREQ2
BOOL_IND_INVERTEROVERLOAD = 122  # era BOOL_IND_LATROLLLOWER, BOOL_IND_EMGCYPHOTOCELLREQ3
BOOL_IND_LEFTSUPPINTERLOCK = 123  # era BOOL_IND_ANYROLLLOWER, BOOL_IND_EMGCYPHOTOCELLREQ4
BOOL_IND_GREASELEVEL = 124  # era BOOL_IND_EMGCYDOORREQ
BOOL_IND_GREASETR = 125  # era BOOL_IND_EMGCYDOORREQ2
BOOL_IND_STARTSENSOR2 = 126  # era BOOL_IND_EMGCYKE12ERR
BOOL_IND_HOLDTORUNRC2 = 127  # era BOOL_IND_EMGCYKE34ERR
BOOL_IND_TILTBAL = 128  # era BOOL_IND_EMGCYHOLDTORUNERR
BOOL_IND_FREE_129 = 129  # era BOOL_IND_SDOSTART, era BOOL_IND_EMGCYHWERR
BOOL_IND_FREE_130 = 130  # era BOOL_IND_SDOBUSY, era BOOL_IND_EMGCYLOCKHWMSG
BOOL_IND_FREE_131 = 131  # era BOOL_IND_SDOOK
BOOL_IND_RIGHTSUPPINTERLOCK = 132
BOOL_IND_APPLYROT = 133
BOOL_IND_REPEATEND = 134
BOOL_IND_AUTOSTARTINGBLINK = 71  # era BOOL_IND_EMGCYTOT
BOOL_IND_AUTOSTARTING = 110  # era BOOL_IND_EMGCYBUZZER
BOOL_IND_SYNCLOADOUT = 136
BOOL_IND_SYNCUNLOADIN = 137
BOOL_IND_SYNCUNLOADOUT = 138
BOOL_IND_SYNCSTARTIN = 139
BOOL_IND_SYNCSTARTOUT = 140
BOOL_IND_SYNCRELOADENAB = 141  # abilitazione stazione alternativa
BOOL_IND_SYNCRELOADALT = 142  # stazione alternativa selezionata
BOOL_IND_SYNCLOADPARAM = 143
BOOL_IND_SYNCLOADIN = 135
MAX_STATOBOOL = 151  # era 135 in v.0.25.42, era 127 in v.0.18
BOOL_IND_SYNCCONFIG1 = 144
BOOL_IND_SYNCCONFIG1ALT = 145
BOOL_IND_APPLYRESET = 146
BOOL_IND_DISTMEM = 147
BOOL_IND_DISTADJ = 148
BOOL_IND_PARTAUTO = 149
BOOL_IND_PARTAUTORUNNING = 150
BOOL_IND_FREE_151 = 151
STATOINT_IND_STATO = 0
STATOINT_IND_JOBLASTOP = 1  # era STATOINT_IND_CURRDIAGIND, STATOINT_IND_EMGCYBITS
STATOREAL_IND_SYSPRESS1 = 0
STATOREAL_IND_SYSPRESS2 = 1
STATOREAL_IND_SYSPRESS3 = 2
STATOREAL_IND_PINCHPRESS = 3
STATOREAL_IND_PINCHPRESSMAN = 4
STATOREAL_IND_OILQUALITY = 5  # era STATOREAL_IND_PINCHPRESSPROG
STATOREAL_IND_PINCHPRESSAUTO = 6
STATOREAL_IND_PINCHPRESS2 = 7
STATOREAL_IND_PINCHPRESSMAN2 = 8
STATOREAL_IND_FREE9 = 9  # era STATOREAL_IND_PINCHPRESSPROG2
STATOREAL_IND_PINCHPRESSAUTO2 = 10
STATOREAL_IND_FREE11 = 11  # era STATOREAL_IND_PINCHDELTA
STATOREAL_IND_FREE12 = 12  # era STATOREAL_IND_PINCHDELTAMAN
STATOREAL_IND_FREE13 = 13  # era STATOREAL_IND_PINCHDELTAPROG
STATOREAL_IND_CURRRELROT = 14  # era STATOREAL_IND_PINCHDELTAAUTO
STATOINT_IND_SEQCURRID = 2
STATOINT_IND_STATCURRPOS = 3
STATOINT_IND_CONFIG = 4
STATOINT_IND_STATSTART = 5
STATODINT_IND_FREE = 0
STATODINT_IND_FREE1 = 1
MAX_STATOOUTDINT = 1
MAX_STATOOUTINT = 7
MAX_STATOOUTREAL = 15
STATOINT_IND_LASTWARNING = 6
STATOREAL_IND_CURROT = 15
STATOINT_IND_TABSTATLAST = 7
MAX_TOOLSET = 7
MAX_TOOLSETBOOL = 1
MAX_TOOLSETINT = 3
MAX_TOOLSETREAL = 19  # era 9 prima di v.0.25.45.1.6759 - TiltPreload
TOOLSET_BOOL_FREE_0 = 0
TOOLSET_BOOL_FREE_1 = 1
TOOLSET_INT_ID = 0
TOOLSET_INT_DESCTYPE = 1  # Per gestire stringhe multilingue
TOOLSET_INT_SECTYPE = 2
TOOLSET_INT_NOUT = 3  # 4
TOOLSET_REAL_TRDIAM = 0
TOOLSET_REAL_LRDIAM = 1
TOOLSET_REAL_SRDIAM = 2
TOOLSET_REAL_TROUTDIAM = 3
TOOLSET_REAL_LROUTDIAM = 4
TOOLSET_REAL_SROUTDIAM = 5
TOOLSET_REAL_HEIGHT = 6
TOOLSET_REAL_OFFSET = 7
TOOLSET_REAL_FREE_8 = 8
TOOLSET_REAL_FREE_9 = 9
MAX_TOOLSETOUTPUT = 3  # 4 output rotazione
MAX_TOOLSETOUTPUTINT = 1
MAX_TOOLSETOUTPUTDINT = 7
TOOLSETOUTPUT_INT_AXIS = 0
TOOLSETOUTPUT_INT_IND = 1
TOOLSETOUTPUT_DINT_SCALEMIN1 = 0
TOOLSETOUTPUT_DINT_SCALEMAX1 = 1
TOOLSETOUTPUT_DINT_SCALEMIN2 = 2
TOOLSETOUTPUT_DINT_SCALEMAX2 = 3
TOOLSETOUTPUT_DINT_SCALEMIN1H = 4
TOOLSETOUTPUT_DINT_SCALEMAX1H = 5
TOOLSETOUTPUT_DINT_SCALEMIN2H = 6
TOOLSETOUTPUT_DINT_SCALEMAX2H = 7
TOOLSET_REAL_TILTMAX = 10
TOOLSET_REAL_TILTHH = 11
TOOLSET_REAL_TILTH = 12
TOOLSET_REAL_TILTL = 13
TOOLSET_REAL_TILTLL = 14
TOOLSET_REAL_TILTMIN = 15
TOOLSET_REAL_FREE_16 = 16
TOOLSET_REAL_FREE_17 = 17
TOOLSET_REAL_FREE_18 = 18
TOOLSET_REAL_FREE_19 = 19
MAX_TOOLSETREAL_OLD = 9
ERR_NONE = 0
ERR_FILENAME = 1
ERR_NOHYPHENS = 2
HDR_PROG_SYS = 0
HDR_PROG_PC = 1
HDR_PROG_PLC = 2
HDR_CONFIG = 3
STG_HEADER = 1
STG_SETTING = 2
STG_MOTORSEL = 3
STG_HMIDI = 4
STG_HMIAI = 5
TYPE_NONE = 0
TYPE_PASS = 1
TYPE_PAS = 2
TYPE_4HEL = 4
TYPE_RCMI = 5
TYPE_R = 6
TYPE_4R = 7
TYPE_HAV = 9
TYPE_4HEP = 3
HDR_SETTINGS = 4
HEADER_SN = 0
HEADER_FILETYPE = 1
HEADER_TYPEVERSION = 2
HEADER_FILEVERSION = 3
HDR_MAT = 5
HDR_TOOLSET = 6
HDR_IOTSETTINGS = 7  # No Header - iot-settings.yaml (RSM)
HDR_JOB = 8  # No Header - lavorazioni.csv
HDR_CAPACITY = 9
HDR_WT = 10
HDR_CALC = 11
ERR_WRITE = 3
HDR_SYNCLDR = 12
HMIPAGE_JOB_REQ = 583
HMIPAGE_SYNCLOADER_MAIN = 590
HMIPAGE_CONFIG_PARAMSSYNC = 1139
HMIPAGE_EYEBEND_KEYENCE_DIST = 821
HMIPAGE_DIST_AUTO = 803
TABSTAT_FIRST_R = 3
CMDINT_CURRIND = 12  # per AlarmTest e MaintReset
COD_APPLYROT = 3033
COD_SYNCLOADSEND = 3170
COD_SYNCLOADRECV = 3171
COD_SYNCUNLOADSEND = 3172
COD_SYNCUNLOADRECV = 3173
COD_SYNCSTARTSEND = 3174
COD_SYNCSTARTRECV = 3175
RT_C0 = 0  # 0 centratori - solo RT - 6703
COD_APPLYRESET = 3034
COD_CHECKDISTMEM = 3157  # reset distanza iniziale
COD_CHECKDISTADJ = 3158  # setta distanza in funzione della misura
COD_REALIGN = 3301
BOOL_IND_RCBDOWN_V25 = 102  # usato da v.26 per compatibilità v. precedenti
BOOL_IND_RCBUP_V25 = 101  # usato da v.26 per compatibilità v. precedenti
BOOL_IND_RCLDOWN_V25 = 98  # usato da v.26 per compatibilità v. precedenti
BOOL_IND_RCLUP_V25 = 97  # usato da v.26 per compatibilità v. precedenti
BOOL_IND_RCRDOWN_V25 = 100  # usato da v.26 per compatibilità v. precedenti
BOOL_IND_RCRUP_V25 = 99  # usato da v.26 per compatibilità v. precedenti
BOOL_IND_RCTLEFT_V25 = 103  # usato da v.26 per compatibilità v. precedenti
BOOL_IND_RCTRIGHT_V25 = 104  # usato da v.26 per compatibilità v. precedenti


