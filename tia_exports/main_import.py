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
    """Valore di default per i tipi base e array nei TYPE UDT."""
    original = typ.strip()
    tlower = original.lower()

    array_re = re.compile(
        r'array\s*\[\s*"?([A-Za-z_]\w*|\d+)"?\s*\.\.\s*"?([A-Za-z_]\w*|\d+)"?\s*\]\s*of\s*(\w+)',
        re.IGNORECASE
    )
    am = array_re.match(original)
    if am:
        min_raw, max_raw, base = am.groups()
        base_type = base.lower()

        if "bool" in base_type:
            base_default = "False"
        elif any(x in base_type for x in ("sint","usint","int","dint","lint","ulint","uint","udint","byte","word","dword")):
            base_default = "-1"
        elif "real" in base_type or "lreal" in base_type:
            base_default = "0.0"
        else:
            base_default = "None"

        length_expr = f"({max_raw} + 1)" if min_raw == "0" else f"(({max_raw}) - ({min_raw}) + 1)"
        return f"[{base_default}] * {length_expr}"

    if "bool" in tlower:
        return "False"
    if any(x in tlower for x in ("sint","usint","int","dint","lint","ulint","uint","udint","byte","word","dword")):
        return "-1"
    if any(x in tlower for x in ("lreal", "real")):
        return "0.0"
    return "None"


# ==============================
# 🔸 UDT (.udt)
# ==============================
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
        out.write(f"class {class_name}:\n")
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
def process_db_file(filepath: str, out):
    filename = os.path.basename(filepath)
    class_name = sanitize_class_name(os.path.splitext(filename)[0])

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Rimuovi i metadati { ... }
    content = re.sub(r'\{[^{}]*\}', '', content)

    # Estrai blocco VAR...END_VAR
    var_m = re.search(r'\bVAR\b(.*?)\bEND_VAR\b', content, flags=re.DOTALL | re.IGNORECASE)
    if not var_m:
        print(f"⚠️ Nessun blocco VAR trovato in {filename}.")
        return

    decls = parse_decls_from_struct(var_m.group(1))
    if not decls:
        print(f"⚠️ Nessuna variabile parsata in {filename}.")
        return

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

        # Array di UDT?
        udt_match = udt_array_re.match(var_type)
        if udt_match:
            min_raw, max_raw, udt_class = udt_match.groups()
            length_expr = f"({max_raw} + 1)" if min_raw == "0" else f"(({max_raw}) - ({min_raw}) + 1)"
            out.write(f"        self.{safe_name} = [{udt_class}() for _ in range{length_expr}]{comment_str}\n")
            out.write(f"        self._defaults['{safe_name}'] = [{udt_class}() for _ in range{length_expr}]\n")
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
    print(EXPORTS_DIR, ' > ', OUTPUT_FILE)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# Auto-generato da main_import.py\n\n")
        for filename in os.listdir(EXPORTS_DIR):
            filepath = os.path.join(EXPORTS_DIR, filename)
            lower = filename.lower()
            if lower.endswith(".udt"):
                process_udt_file(filepath, out)
            elif lower.endswith(".db"):
                process_db_file(filepath, out)
            elif lower.endswith(".xlsx"):
                process_excel(filepath, out)
    print(f"✅ File generato: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
