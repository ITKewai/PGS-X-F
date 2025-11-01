# usa il modulo come sorgente unico
from importlib import import_module
import utils.exports.tia_constants as tc

AXIS_GROUP_STEP = 64
BASE_AXIS = 2048

ALARM_GROUP_STEP = 256
BASE_ALARM = 16384


def _build_groups(module, prefix: str, base: int, step: int):
    items = [
        (name[len(prefix):], getattr(module, name))
        for name in dir(module)
        if name.startswith(prefix)
           and isinstance(getattr(module, name), int)
           and getattr(module, name) >= 0
    ]
    items.sort(key=lambda kv: kv[1])
    order = [label for label, _ in items]
    base_map = {label: base + i * step for i, label in enumerate(order)}
    return order, base_map


AXIS_GROUPS_ORDER, AXIS_GROUP_BASE = _build_groups(tc, "IO_SYSAXIS_", BASE_AXIS, AXIS_GROUP_STEP)
ALARM_GROUPS_ORDER, ALARM_GROUP_BASE = _build_groups(tc, "IO_SYSALARM_", BASE_ALARM, ALARM_GROUP_STEP)
