#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
EXPORTS_DIR = os.path.join(BASE_DIR, "")
OUTPUT_FILE = os.path.join(BASE_DIR, "tia_constants.py")


def get_prefix(name: str) -> str:
    parts = name.split("_")
    return "_".join(parts[:2]) if len(parts) > 1 else name


def process_excel(filepath: str, out):
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

        class_name = os.path.splitext(filename)[0]
        out.write(f"# Estratto da: {filename}\n")
        out.write(f"class {sanitize_class_name(class_name)}:\n")

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


def sanitize_class_name(name: str) -> str:
    # Classe Python valida
    clean = re.sub(r'[^0-9a-zA-Z_]', '_', name)
    if re.match(r'^\d', clean):
        clean = f"_{clean}"
    return clean


def parse_tia_db_text(text: str):
    """Ritorna lista [(var_name, var_type)] da blocchi STRUCT o VAR in un .db TIA (testo)."""
    if text and text[0] == '\ufeff':  # BOM
        text = text[1:]

    # Colleziona tutte le regioni dichiarative
    regions = []

    # STRUCT ... END_STRUCT (possono essere più)
    for m in re.finditer(r'STRUCT(.*?)END_STRUCT', text, re.DOTALL | re.IGNORECASE):
        regions.append(m.group(1))

    # VAR ... END_VAR (VAR, VAR_RETAIN, VAR_TEMP, ecc.)
    for m in re.finditer(r'\bVAR(?:\s+\w+)?\b(.*?)\bEND_VAR\b', text, re.DOTALL | re.IGNORECASE):
        regions.append(m.group(1))

    # Se non ha trovato nulla, prova tutto il testo (best effort)
    if not regions:
        regions = [text]

    decls = []
    for region in regions:
        # Rimuovi commenti SCL: (* ... *) e // fino a fine riga
        region = re.sub(r'\(\*.*?\*\)', '', region, flags=re.DOTALL)
        region = re.sub(r'//.*?$', '', region, flags=re.MULTILINE)

        # name {attrs}? : type ;
        pat = re.compile(r'\s*([A-Za-z_]\w*)\s*(\{[^}]*\})?\s*:\s*([^;]+);', re.MULTILINE)
        for m in pat.finditer(region):
            name = m.group(1)
            typ = re.sub(r'\s+', ' ', m.group(3).strip())
            decls.append((name, typ))

    return decls


def process_tia_db(filepath: str, out):
    filename = os.path.basename(filepath)
    class_name = os.path.splitext(filename)[0]
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        decls = parse_tia_db_text(content)

        out.write(f"# Estratto da: {filename}\n")
        out.write(f"class {sanitize_class_name(class_name)}:\n")

        if not decls:
            print(f"⚠️ Nessuna dichiarazione trovata in {filename}")
            out.write("    pass\n\n")
            return

        for var_name, var_type in decls:
            out.write(f"    {var_name.upper()} = '{var_type}'\n")

        out.write("\n\n")
    except Exception as e:
        print(f"❌ Errore leggendo {filename}: {e}")


def main():
    print(EXPORTS_DIR, ' > ', OUTPUT_FILE)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# Auto-generato da main_import.py\n\n")
        for filename in os.listdir(EXPORTS_DIR):
            filepath = os.path.join(EXPORTS_DIR, filename)
            if filename.endswith(".xlsx"):
                process_excel(filepath, out)
            elif filename.endswith(".db"):
                process_tia_db(filepath, out)
    print(f"✅ File generato: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
