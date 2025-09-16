#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
EXPORTS_DIR = os.path.join(BASE_DIR, "")
OUTPUT_FILE = os.path.join(BASE_DIR, "tia_constants.py")


def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for filename in os.listdir(EXPORTS_DIR):
            if filename.endswith(".xlsx"):
                filepath = os.path.join(EXPORTS_DIR, filename)
                try:
                    # Carica il foglio "Constants"
                    df = pd.read_excel(filepath, sheet_name="Constants")

                    # Ordina per colonna "Value" (se esiste)
                    if "Value" in df.columns:
                        df = df.sort_values(by="Value", ascending=True, na_position="last")

                    # Nome classe = nome file senza estensione
                    class_name = os.path.splitext(filename)[0]
                    out.write(f"class {class_name}:\n")

                    found_any = False
                    for _, row in df.iterrows():
                        name = row.get("Name")
                        value = row.get("Value")
                        if pd.notna(name) and pd.notna(value):
                            out.write(f"    {name} = {repr(value)}\n")
                            found_any = True
                    if not found_any:
                        out.write("    pass\n")
                    out.write("\n\n")

                except Exception as e:
                    print(f"Errore leggendo {filename}: {e}")

    print(f"✅ File generato: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
