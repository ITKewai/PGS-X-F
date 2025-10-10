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


def parse_tia_text(text: str):
    """Estrae [(var_name, var_type, comment)] da STRUCT/VAR in file TIA (.db, .udt)."""
    if text and text[0] == '\ufeff':  # BOM
        text = text[1:]

    regions = []
    for m in re.finditer(r'STRUCT(.*?)END_STRUCT', text, re.DOTALL | re.IGNORECASE):
        regions.append(m.group(1))

    for m in re.finditer(r'\bVAR(?:\s+\w+)?\b(.*?)\bEND_VAR\b', text, re.DOTALL | re.IGNORECASE):
        regions.append(m.group(1))

    if not regions:
        regions = [text]

    decls = []
    for region in regions:
        region = re.sub(r'\(\*.*?\*\)', '', region, flags=re.DOTALL)  # (* commenti *)
        # ⚠️ NON rimuoviamo i commenti // qui, li catturiamo con la regex sotto

        pat = re.compile(
            r'\s*([A-Za-z_]\w*)'              # nome variabile
            r'\s*(\{[^}]*\})?\s*:\s*'         # eventuali attributi {...}
            r'([^;]+);'                       # tipo
            r'(?:\s*//\s*(.*))?',             # commento opzionale
            re.MULTILINE
        )
        for m in pat.finditer(region):
            name = m.group(1)
            typ = re.sub(r'\s+', ' ', m.group(3).strip())
            comment = m.group(4).strip() if m.group(4) else ''
            decls.append((name, typ, comment))
    return decls


def tia_type_to_python_default(typ: str):
    """Mappa i tipi TIA → valore di default Python."""
    t = typ.lower()
    if "bool" in t:
        return "False"
    if "int" in t or "dint" in t or "ulint" in t:
        return "-1"
    if "real" in t or "lreal" in t:
        return "0.0"
    return "None"  # fallback per tipi custom


# ==============================
# 🔸 Generazione classi da TIA (.db / .udt)
# ==============================
def process_tia_file(filepath: str, out):
    """Legge file .db o .udt e genera classe Python con __init__ e helper."""
    filename = os.path.basename(filepath)
    class_name = sanitize_class_name(os.path.splitext(filename)[0])

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    decls = parse_tia_text(content)
    out.write(f"# Estratto da: {filename}\n")
    out.write(f"class {class_name}:\n")

    if decls:
        out.write('    """\n')
        out.write(f"    Estratto da: {filename}\n\n")
        out.write("    Attributes:\n")
        for var_name, var_type, var_comment in decls:
            comment_line = f" {var_comment}" if var_comment else ""
            out.write(f"        {var_name} ({var_type}):{comment_line}\n")
        out.write('    """\n')
    else:
        out.write("    pass\n\n")
        return

    # --- init ---
    out.write("    def __init__(self):\n")
    out.write("        self._defaults = {}\n")
    for var_name, var_type, var_comment in decls:
        default_val = tia_type_to_python_default(var_type)
        comment_str = f"  # {var_type}" + (f" // {var_comment}" if var_comment else "")
        out.write(f"        self.{var_name} = {default_val}{comment_str}\n")
        out.write(f"        self._defaults['{var_name}'] = {default_val}\n")
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
# 🔸 Generazione classi da Excel
# ==============================
def process_excel(filepath: str, out):
    return
    filename = os.path.basename(filepath)
    try:
        df = pd.read_excel(filepath, sheet_name="Constants")
        if "Name" not in df.columns or "Value" not in df.columns:
            print(f"⚠️ File {filename} non ha colonne Name/Value valide, skip.")
            return

        df["Prefix"] = df["Name"].apply(lambda x: get_prefix(str(x)))
        df = df.sort_values(by=["Prefix", "Value", "Name"],
                            ascending=[True, True, True],
                            na_position="last")

        class_name = sanitize_class_name(os.path.splitext(filename)[0])
        out.write(f"# Estratto da: {filename}\n")
        out.write(f"class {class_name}:\n")

        found_any = False
        last_prefix = None
        for _, row in df.iterrows():
            name = row.get("Name")
            value = row.get("Value")
            prefix = row.get("Prefix")
            comment = f'  # {row.get("Comment")}' if isinstance(row.get("Comment"), str) else ''
            if pd.notna(name) and pd.notna(value):
                if last_prefix is not None and prefix != last_prefix:
                    out.write("\n")
                out.write(f"    {name} = {repr(value)}{comment}\n")
                last_prefix = prefix
                found_any = True

        if not found_any:
            out.write("    pass\n")
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
            if filename.endswith(".xlsx"):
                process_excel(filepath, out)
            elif filename.endswith(".db") or filename.endswith(".udt"):
                process_tia_file(filepath, out)
    print(f"✅ File generato: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
