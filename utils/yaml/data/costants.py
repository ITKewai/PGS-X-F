# --- Indici attesi nella struttura obj>input ---
AXIS_GROUP_STEP = 64  # numero max assi per gruppo DI_GET[FC100]
BASE_AXIS = 2048  # DI_GET[FC100]


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
