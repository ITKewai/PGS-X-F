#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
EXPORTS_DIR = os.path.join(BASE_DIR, "")
OUTPUT_FILE = os.path.join(BASE_DIR, "tia_constants.py")


# ==============================
# 🔸 Utility
# ==============================
RESERVED_NAMES = {"in", "class", "def", "return", "global", "lambda"}


def get_prefix(name: str) -> str:
    parts = name.split("_")
    return "_".join(parts[:2]) if len(parts) > 1 else name


def sanitize_class_name(name: str) -> str:
    """Rende il nome compatibile con Python (niente spazi o simboli strani)."""
    clean = re.sub(r'[^0-9a-zA-Z_]', '_', name)
    if re.match(r'^\d', clean):
        clean = f"_{clean}"
    return clean


def parse_decls_from_struct(struct_text: str):
    """
    Estrae [(var_name, var_type, comment)] dalla porzione interna di una STRUCT/VAR.
    Mantiene i commenti // come description a destra.
    """
    decls = []
    if not struct_text:
        return decls

    pat = re.compile(
        r'\s*([A-Za-z_]\w*)'              # nome variabile
        r'\s*(\{[^}]*\})?\s*:\s*'         # ignora graffe
        r'([^;]+);'                       # tipo
        r'(?:\s*//\s*(.*))?',             # commento opzionale
        re.MULTILINE
    )
    for m in pat.finditer(struct_text):
        name = m.group(1)
        typ = re.sub(r'\s+', ' ', m.group(3).strip())
        comment = m.group(4).strip() if m.group(4) else ''
        decls.append((name, typ, comment))
    return decls


def tia_type_to_python_default(typ: str):
    """Valore di default per i tipi base e array nei TYPE UDT/DB."""
    original = typ.strip()
    tlower = original.lower()

    # STRING[n] oppure STRING["NOME_COSTANTE"]
    string_re = re.compile(
        r'string\s*\[\s*"?([A-Za-z_]\w*|\d+)"?\s*\]',
        re.IGNORECASE
    )
    sm = string_re.fullmatch(original)
    if sm:
        strlen_raw = sm.group(1)
        return f'" " * ({strlen_raw})'

    array_re = re.compile(
        r'array\s*\[\s*"?([A-Za-z_]\w*|\d+)"?\s*\.\.\s*"?([A-Za-z_]\w*|\d+)"?\s*\]\s*of\s*(.+)',
        re.IGNORECASE
    )
    am = array_re.fullmatch(original)
    if am:
        min_raw, max_raw, base = am.groups()
        base = base.strip()
        base_type = base.lower()

        # Array di STRING[n] o STRING["COSTANTE"]
        string_array_re = re.compile(
            r'string\s*\[\s*"?([A-Za-z_]\w*|\d+)"?\s*\]',
            re.IGNORECASE
        )
        sam = string_array_re.fullmatch(base)

        if sam:
            strlen_raw = sam.group(1)
            base_default = f'" " * {strlen_raw}'
        else:
            # Array di UDT: Array[0.."MAX_STAT"] of "Type_Stat"
            udt_m = re.fullmatch(r'"?(Type_\w+)"?', base, re.IGNORECASE)
            if udt_m:
                base_default = udt_m.group(1)
            elif "bool" in base_type:
                base_default = "False"
            elif any(x in base_type for x in ("sint", "usint", "int", "dint", "lint", "ulint", "uint", "udint", "byte", "word", "dword")):
                base_default = "-1"
            elif "real" in base_type or "lreal" in base_type:
                base_default = "0.0"
            else:
                base_default = "None"

        length_expr = f"({max_raw} + 1)" if min_raw == "0" else f"(({max_raw}) - ({min_raw}) + 1)"
        return f"[{base_default}] * {length_expr}"

    if "bool" in tlower:
        return "False"
    if any(x in tlower for x in ("sint", "usint", "int", "dint", "lint", "ulint", "uint", "udint", "byte", "word", "dword")):
        return "-1"
    if any(x in tlower for x in ("lreal", "real")):
        return "0.0"

    return "None"


# ==============================
# 🔸 UDT (.udt)
# ==============================
def tia_udt_class_name(typ: str):
    m = re.match(r'\s*"?(Type_\w+)"?\s*$', typ, re.IGNORECASE)
    return sanitize_class_name(m.group(1)) if m else None


def tia_value_to_python(value: str) -> str:
    value = value.strip()

    if re.fullmatch(r"'[^']*'", value):
        return value
    if value.upper() == "TRUE":
        return "True"
    if value.upper() == "FALSE":
        return "False"
    if re.fullmatch(r'[-+]?\d+', value):
        return value
    if re.fullmatch(r'[-+]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][-+]?\d+)?', value):
        return value

    # Literali TIA non validi in Python (es. T#0MS) -> stringa
    return repr(value)


def tia_target_to_python(target: str) -> str:
    target = target.strip()
    target = re.sub(
        r'\b([A-Za-z_]\w*)\b',
        lambda m: f"{m.group(1)}_" if m.group(1) in RESERVED_NAMES else m.group(1),
        target
    )
    return f"self.{target}"


def parse_db_init_assignments(content: str):
    parts = re.split(r'\bBEGIN\b', content, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) < 2:
        return []

    init_section = parts[1]
    assigns = []
    assign_pat = re.compile(r'^\s*(.+?)\s*:=\s*(.+?)\s*;\s*$', re.MULTILINE)
    for m in assign_pat.finditer(init_section):
        assigns.append((m.group(1).strip(), m.group(2).strip()))
    return assigns


def process_udt_file(filepath: str, out):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # Togli commenti TIA (* ... *)
    text = re.sub(r'\(\*.*?\*\)', '', text, flags=re.DOTALL)

    # TYPE ... END_TYPE
    type_pat = re.compile(r'TYPE\s+"?([A-Za-z_]\w*)"?\s*(.*?)\bEND_TYPE\b', re.DOTALL | re.IGNORECASE)
    for type_m in type_pat.finditer(text):
        type_name = type_m.group(1)
        body = type_m.group(2)

        # STRUCT ... END_STRUCT
        struct_m = re.search(r'\bSTRUCT\b(.*?)\bEND_STRUCT\s*;', body, flags=re.DOTALL | re.IGNORECASE)
        if not struct_m:
            continue

        decls = parse_decls_from_struct(struct_m.group(1))
        if not decls:
            continue

        class_name = sanitize_class_name(type_name)
        # out.write(f"# --- TYPE \"{type_name}\" ---\n")
        out.write(f"\nclass {class_name}:\n")
        out.write('    """\n')
        out.write(f"    Estratto da: {filename}\n\n")
        out.write("    Attributes:\n")
        for var_name, var_type, var_comment in decls:
            safe_name = var_name + "_" if var_name in RESERVED_NAMES else var_name
            comment_line = f" {var_comment}" if var_comment else ""
            out.write(f"        {safe_name} ({var_type}):{comment_line}\n")
        out.write('    """\n')

        out.write("    def __init__(self):\n")
        out.write("        self._defaults = {}\n")
        for var_name, var_type, var_comment in decls:
            safe_name = var_name + "_" if var_name in RESERVED_NAMES else var_name
            default_val = tia_type_to_python_default(var_type)
            comment_str = f"  # {var_type}" + (f" // {var_comment}" if var_comment else "")
            out.write(f"        self.{safe_name} = {default_val}{comment_str}\n")
            out.write(f"        self._defaults['{safe_name}'] = {default_val}\n")
        out.write("\n")

        out.write("    def to_dict(self):\n")
        out.write("        return {k: getattr(self, k) for k in self._defaults.keys()}\n\n")

        out.write("    def reset(self):\n")
        out.write("        for k, v in self._defaults.items():\n")
        out.write("            setattr(self, k, v)\n\n")

        out.write("    def __repr__(self):\n")
        out.write("        fields = ', '.join(f\"{k}={getattr(self, k)}\" for k in self._defaults.keys())\n")
        out.write(f"        return f\"<{class_name} {{fields}}>\"\n\n\n")


# ==============================
# 🔸 DB (.db)
# ==============================
def is_redundant_init_assignment(target: str, py_value: str, decls):
    """
    Ritorna True se un'assegnazione nel BEGIN è già coperta dal default
    generato dalla dichiarazione VAR.

    Esempio:
        AxisFunInd[0] := -1
    viene saltato se:
        AxisFunInd : Array[0.."MAX_ASSEFUNIND"] of Int
    genera già:
        self.AxisFunInd = [-1] * (MAX_ASSEFUNIND + 1)
    """

    # Caso array semplice: NomeArray[123]
    m = re.match(r'^([A-Za-z_]\w*)\s*\[.+\]$', target.strip())
    if not m:
        return False

    array_name = m.group(1)

    for var_name, var_type, _ in decls:
        if var_name != array_name:
            continue

        default_val = tia_type_to_python_default(var_type)

        # Array di Int / DInt / ecc.
        if default_val.startswith("[-1]") and py_value == "-1":
            return True

        # Array di Bool
        if default_val.startswith("[False]") and py_value == "False":
            return True

        # Array di Real
        if default_val.startswith("[0.0]") and py_value in ("0.0", "0"):
            return True

        # Array di stringhe vuote/spazi: non lo salto qui in modo aggressivo,
        # perché '' e " " * DIM_STRING... non sono semanticamente identici.
        # Se vuoi saltare anche gli '', si può aggiungere una regola dedicata.

    return False


def process_db_file(filepath: str, out):
    """Versione 0.2: inizializza anche i valori presenti nel blocco BEGIN del DB."""
    filename = os.path.basename(filepath)
    class_name = sanitize_class_name(os.path.splitext(filename)[0])

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        raw_content = f.read()

    # Rimuovi i metadati { ... }
    content = re.sub(r'\{[^{}]*\}', '', raw_content)

    # Considera solo la sezione dichiarativa del DB (prima di BEGIN)
    decl_section = re.split(r'\bBEGIN\b', content, maxsplit=1, flags=re.IGNORECASE)[0]

    # Estrai TUTTI i blocchi VAR ... END_VAR, inclusi VAR RETAIN
    var_pat = re.compile(r'\bVAR(?:\s+RETAIN)?\b(.*?)\bEND_VAR\b', re.DOTALL | re.IGNORECASE)

    decls = []
    for var_m in var_pat.finditer(decl_section):
        decls.extend(parse_decls_from_struct(var_m.group(1)))

    if not decls:
        print(f"⚠️ Nessuna variabile parsata in {filename}.")
        return

    # Estrai anche le inizializzazioni dal BEGIN
    init_assignments = parse_db_init_assignments(content)

    out.write(f"# --- DB {filename} ---\n")
    out.write(f"class {class_name}:\n")
    out.write("    def __init__(self):\n")
    out.write("        self._defaults = {}\n")

    # Regex per array di UDT
    udt_array_re = re.compile(
        r'array\s*\[\s*"?([A-Za-z_]\w*|\d+)"?\s*\.\.\s*"?([A-Za-z_]\w*|\d+)"?\s*\]\s*of\s*"?(Type_\w+)"?',
        re.IGNORECASE
    )

    for var_name, var_type, var_comment in decls:
        safe_name = var_name + "_" if var_name in RESERVED_NAMES else var_name
        comment_str = f"  # {var_type}" + (f" // {var_comment}" if var_comment else "")

        # Array di UDT
        udt_match = udt_array_re.match(var_type)
        if udt_match:
            min_raw, max_raw, udt_class = udt_match.groups()
            length_expr = f"({max_raw} + 1)" if min_raw == "0" else f"(({max_raw}) - ({min_raw}) + 1)"
            out.write(f"        self.{safe_name} = [{udt_class}() for _ in range{length_expr}]{comment_str}\n")
            out.write(f"        self._defaults['{safe_name}'] = self.{safe_name}\n")
            continue

        # UDT semplice
        udt_class = tia_udt_class_name(var_type)
        if udt_class:
            out.write(f"        self.{safe_name} = {udt_class}(){comment_str}\n")
            out.write(f"        self._defaults['{safe_name}'] = self.{safe_name}\n")
            continue

        # Array di tipi base
        if var_type.lower().startswith("array"):
            default_val = tia_type_to_python_default(var_type)
            out.write(f"        self.{safe_name} = {default_val}{comment_str}\n")
            out.write(f"        self._defaults['{safe_name}'] = {default_val}\n")
            continue

        # Tipo semplice
        default_val = tia_type_to_python_default(var_type)
        out.write(f"        self.{safe_name} = {default_val}{comment_str}\n")
        out.write(f"        self._defaults['{safe_name}'] = {default_val}\n")

    # Applica i valori iniziali presenti nel BEGIN
    # saltando quelli identici al default già generato
    if init_assignments:
        out.write("\n")
        for target, value in init_assignments:
            py_target = tia_target_to_python(target)
            py_value = tia_value_to_python(value)

            if is_redundant_init_assignment(target, py_value, decls):
                continue

            out.write(f"        {py_target} = {py_value}\n")

    out.write("\n")


# ==============================
# 🔸 Excel (costanti)
# ==============================
def process_excel(filepath: str, out):
    filename = os.path.basename(filepath)
    try:
        df = pd.read_excel(filepath, sheet_name="Constants")
        if "Name" not in df.columns or "Value" not in df.columns:
            print(f"⚠️ File {filename} non ha colonne Name/Value valide, skip.")
            return

        out.write(f"# ===== Costanti da: {filename} =====\n")
        for _, row in df.iterrows():
            name = row.get("Name")
            value = row.get("Value")
            comment = row.get("Comment")
            if pd.notna(name) and pd.notna(value):
                cmt = f"  # {comment}" if isinstance(comment, str) else ""
                out.write(f"{name} = {int(value)}{cmt}\n")
        out.write("\n\n")
    except Exception as e:
        print(f"❌ Errore leggendo {filename}: {e}")


# ==============================
# 🔸 Main
# ==============================
def main():
    print("=== Generazione automatica tia_constants per ogni cartella valida ===")

    # Trova tutte le sottocartelle
    subfolders = [
        d for d in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, d)) and not d.startswith('.')
    ]

    if not subfolders:
        print("❌ Nessuna sottocartella trovata.")
        return

    for folder in subfolders:
        exports_dir = os.path.join(BASE_DIR, folder)

        # Cerca file validi nella cartella
        file_list = os.listdir(exports_dir)
        valid_files = [
            f for f in file_list
            if f.lower().endswith((".udt", ".db", ".xlsx"))
        ]

        # Se la cartella non contiene file validi → ignora
        if not valid_files:
            print(f"⚠️  Ignorata: {folder} (nessun file udt/db/xlsx)")
            continue

        # Nome file output con versione
        output_file = os.path.join(
            exports_dir,
            f"tia_constants_{folder}.py"
        )

        print(f"\n📂 Cartella valida: {folder}")
        print(f"   → Generazione file: {output_file}")

        with open(output_file, "w", encoding="utf-8") as out:
            out.write("# Auto-generato da main_import.py\n")
            out.write(f"__version__ = '{folder.replace('_', '.')}'\n\n")

            for filename in valid_files:
                filepath = os.path.join(exports_dir, filename)
                lower = filename.lower()

                if lower.endswith(".udt"):
                    process_udt_file(filepath, out)
                elif lower.endswith(".db"):
                    process_db_file(filepath, out)
                elif lower.endswith(".xlsx"):
                    process_excel(filepath, out)

        print(f"   ✅ Creato: {output_file}")

    print("\n🎉 Generazione completata!")


if __name__ == "__main__":
    main()
