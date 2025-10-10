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
def get_prefix(name: str) -> str:
    parts = name.split("_")
    return "_".join(parts[:2]) if len(parts) > 1 else name


def sanitize_class_name(name: str) -> str:
    """Rende il nome compatibile con Python (niente spazi o simboli strani)."""
    clean = re.sub(r'[^0-9a-zA-Z_]', '_', name)
    if re.match(r'^\d', clean):
        clean = f"_{clean}"
    return clean


def split_type_blocks(text: str):
    """
    Ritorna una lista di (type_name, struct_body, full_block_text) per ogni TYPE ... END_TYPE nel file.
    - struct_body è il contenuto tra STRUCT ... END_STRUCT; (senza i delimitatori)
    - Se non trova STRUCT, struct_body è la porzione tra VAR ... END_VAR o stringa vuota
    """
    if text and text[:1] == '\ufeff':
        text = text[1:]

    # Togli commenti TIA in stile (* ... *)
    no_block_comments = re.sub(r'\(\*.*?\*\)', '', text, flags=re.DOTALL)

    blocks = []
    # Match TYPE "Name" ... END_TYPE
    type_pat = re.compile(r'TYPE\s+"?([A-Za-z_]\w*)"?\s*(.*?)\bEND_TYPE\b', re.DOTALL | re.IGNORECASE)
    for m in type_pat.finditer(no_block_comments):
        type_name = m.group(1)
        body = m.group(2)

        # Estrarre STRUCT ... END_STRUCT; se presente
        struct_m = re.search(r'\bSTRUCT\b(.*?)\bEND_STRUCT\s*;', body, flags=re.DOTALL | re.IGNORECASE)
        if struct_m:
            struct_body = struct_m.group(1)
        else:
            # alternativa: blocchi VAR ... END_VAR
            var_m = re.search(r'\bVAR(?:\s+\w+)?\b(.*?)\bEND_VAR\b', body, flags=re.DOTALL | re.IGNORECASE)
            struct_body = var_m.group(1) if var_m else ""

        blocks.append((type_name, struct_body.strip(), body))
    return blocks


def parse_decls_from_struct(struct_text: str):
    """
    Estrae [(var_name, var_type, comment)] dalla porzione interna di una STRUCT/VAR.
    Mantiene i commenti // come description a destra.
    """
    decls = []
    if not struct_text:
        return decls

    # NON rimuoviamo i commenti //, li catturiamo con la regex
    pat = re.compile(
        r'\s*([A-Za-z_]\w*)'              # nome variabile
        r'\s*(\{[^}]*\})?\s*:\s*'         # eventuali attributi {...}
        r'([^;]+);'                       # tipo (fino al ;)
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
    """Mappa i tipi TIA → valore di default Python.
    - Supporta Array[MIN..MAX] of <type>, preservando il casing di MIN/MAX
    - MIN può essere 0, numero, o identificatore (es. MIN_SMTH)
    - Genera liste come [default] * ((MAX - MIN) + 1)  oppure semplifica a (MAX + 1) se MIN == 0
    """
    original = typ.strip()
    tlower = original.lower()

    # --- Array ---
    # Esempi matchati:
    # Array[0.."MAX_OUTPUTDINT"] of DInt
    # ARRAY [ 0 .. MAX_ABC ] OF REAL
    # Array["MIN_IDX".."MAX_IDX"] of Bool
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

        # Costruisci espressione di lunghezza
        if min_raw == "0" or min_raw == "0.0":
            length_expr = f"({max_raw} + 1)"
        else:
            length_expr = f"(({max_raw}) - ({min_raw}) + 1)"

        return f"[{base_default}] * {length_expr}"

    # --- Tipi scalari ---
    if "bool" in tlower:
        return "False"
    if any(x in tlower for x in ("sint","usint","int","dint","lint","ulint","uint","udint","byte","word","dword")):
        return "-1"
    if any(x in tlower for x in ("lreal", "real")):
        return "0.0"
    return "None"  # fallback


# ==============================
# 🔸 Generazione classi da TIA (.db / .udt)
# ==============================
def process_tia_file(filepath: str, out):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    type_blocks = split_type_blocks(content)
    if not type_blocks:
        print(f"⚠️ Nessun TYPE trovato in {filename}.")
        return

    out.write(f"# ===== File: {filename} =====\n\n")

    for type_name, struct_body, _full in type_blocks:
        # Solo per sicurezza: nomi python-safe (ma di default manteniamo quello TIA)
        class_name = sanitize_class_name(type_name)

        decls = parse_decls_from_struct(struct_body)

        out.write(f"# --- TYPE \"{type_name}\" ---\n")
        out.write(f"class {class_name}:\n")

        if decls:
            out.write('    """\n')
            out.write(f"    Estratto da: {filename}\n\n")
            out.write("    Attributes:\n")
            for var_name, var_type, var_comment in decls:
                RESERVED = {"in", "class", "def", "return", "global", "lambda", ...}

                if var_name in RESERVED:
                    safe_name = var_name + "_"
                else:
                    safe_name = var_name

                comment_line = f" {var_comment}" if var_comment else ""
                out.write(f"        {safe_name} ({var_type}):{comment_line}\n")
            out.write('    """\n')
        else:
            out.write("    pass\n\n")
            continue

        # --- init ---
        out.write("    def __init__(self):\n")
        out.write("        self._defaults = {}\n")
        for var_name, var_type, var_comment in decls:
            default_val = tia_type_to_python_default(var_type)
            RESERVED = {"in", "class", "def", "return", "global", "lambda", ...}

            if var_name in RESERVED:
                safe_name = var_name + "_"
            else:
                safe_name = var_name

            comment_str = f"  # {var_type}" + (f" // {var_comment}" if var_comment else "")
            out.write(f"        self.{safe_name} = {default_val}{comment_str}\n")
            out.write(f"        self._defaults['{safe_name}'] = {default_val}\n")

        out.write("\n")

        # --- to_dict ---
        out.write("    def to_dict(self):\n")
        out.write("        \"\"\"Ritorna un dizionario con tutti i campi attuali.\"\"\"\n")
        out.write("        return {k: getattr(self, k) for k in self._defaults.keys()}\n\n")

        # --- reset ---
        out.write("    def reset(self):\n")
        out.write("        \"\"\"Resetta tutti i campi ai valori di default.\"\"\"\n")
        out.write("        for k, v in self._defaults.items():\n")
        out.write("            setattr(self, k, v)\n\n")

        # --- repr ---
        out.write("    def __repr__(self):\n")
        out.write("        fields = ', '.join(f\"{k}={getattr(self, k)}\" for k in self._defaults.keys())\n")
        out.write(f"        return f\"<{class_name} {{fields}}>\"\n\n\n")


# ==============================
# 🔸 Generazione da Excel (opzionale)
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
            value = int(row.get("Value"))
            comment = row.get("Comment")
            if pd.notna(name) and pd.notna(value):
                cmt = f"  # {comment}" if isinstance(comment, str) else ""
                out.write(f"{name} = {repr(value)}{cmt}\n")
        out.write("\n\n")
    except Exception as e:
        print(f"❌ Errore leggendo {filename}: {e}")


# ==============================
# 🔸 Main
# ==============================
def main():
    print(EXPORTS_DIR, ' > ', OUTPUT_FILE)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# Auto-generato da main_import_.py\n\n")
        for filename in os.listdir(EXPORTS_DIR):
            filepath = os.path.join(EXPORTS_DIR, filename)
            if filename.lower().endswith(".xlsx"):
                process_excel(filepath, out)
            elif filename.lower().endswith(".db") or filename.lower().endswith(".udt"):
                process_tia_file(filepath, out)
    print(f"✅ File generato: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
