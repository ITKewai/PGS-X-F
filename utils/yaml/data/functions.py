import utils.exports.tia_constants

PREFIX = "IO_SYSTYPE_"

# prendi tutte le costanti IO_SYSTYPE_* dal modulo
pairs = {
    name[len(PREFIX):]: getattr(utils.exports.tia_constants, name)
    for name in dir(utils.exports.tia_constants)
    if name.startswith(PREFIX)
}

# se vuoi tener fuori qualcosa (es. BOOLSYSTEM), filtra qui
EXCLUDE = set()  # {"BOOLSYSTEM"}
pairs = {k: v for k, v in pairs.items() if k not in EXCLUDE}

# ordina per valore così è deterministico
SYSTEM_TYPE = dict(sorted(pairs.items(), key=lambda kv: kv[1]))
SYSTEM_TYPE_REV = {v: k for k, v in SYSTEM_TYPE.items()}