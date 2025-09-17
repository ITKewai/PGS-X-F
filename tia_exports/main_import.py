#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
EXPORTS_DIR = os.path.join(BASE_DIR, "")
OUTPUT_FILE = os.path.join(BASE_DIR, "tia_constants.py")


def get_prefix(name: str) -> str:
    """
    Ritorna il prefisso per raggruppare le costanti.
    Usa tutto fino al secondo '_' (es. IO_TYPE_X -> IO_TYPE).
    """
    parts = name.split("_")
    return "_".join(parts[:2]) if len(parts) > 1 else name


def main():
    print(EXPORTS_DIR, ' > ',OUTPUT_FILE)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# Auto-generato da tia_vars_export.py\n\n")

        for filename in os.listdir(EXPORTS_DIR):
            if filename.endswith(".xlsx"):
                filepath = os.path.join(EXPORTS_DIR, filename)
                try:
                    df = pd.read_excel(filepath, sheet_name="Constants")

                    if "Name" not in df.columns or "Value" not in df.columns:
                        print(f"⚠️ File {filename} non ha colonne Name/Value valide, salto.")
                        continue

                    # Aggiungi colonna Prefisso
                    df["Prefix"] = df["Name"].apply(lambda x: get_prefix(str(x)))

                    # Ordina per Prefix, Value, Name
                    df = df.sort_values(
                        by=["Prefix", "Value", "Name"],
                        ascending=[True, True, True],
                        na_position="last"
                    )

                    # Nome classe = nome file senza estensione
                    class_name = os.path.splitext(filename)[0]
                    out.write(f"# Estratto da: {filename}\n")
                    out.write(f"class {class_name}:\n")

                    found_any = False
                    last_prefix = None

                    for _, row in df.iterrows():
                        name = row.get("Name")
                        value = row.get("Value")
                        prefix = row.get("Prefix")

                        if pd.notna(name) and pd.notna(value):
                            # Se cambia il prefisso -> riga vuota per separare i gruppi
                            if last_prefix is not None and prefix != last_prefix:
                                out.write("\n")
                            out.write(f"    {name} = {repr(value)}\n")
                            last_prefix = prefix
                            found_any = True

                    if not found_any:
                        out.write("    pass\n")

                    out.write("\n\n")

                except Exception as e:
                    print(f"❌ Errore leggendo {filename}: {e}")

    print(f"✅ File generato: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
