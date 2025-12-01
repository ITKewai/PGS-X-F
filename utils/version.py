#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo che contiene le informazioni di versione e metadati del progetto PGS-X-FindIndex.
"""
import os
import re

__version__ = "1.0.3.4"
__author__ = "ITKewai"
__company__ = ""
__product__ = "PGS-X-FindIndex"
__copyright__ = f"Autore: {__author__} © 2025 {__company__}"


def get_version_info() -> str:
    path = os.path.join("utils", "exports", "tia_constants.py")

    if not os.path.isfile(path):
        return "0.0.0"

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'__version__\s*=\s*["\'](.+?)["\']', content)
    pgs_version = match.group(1) if match else "0.0.0"
    """Ritorna una stringa formattata con le info di versione."""
    return f"{__product__} v{__version__} [PGS {pgs_version}]"


def short() -> str:
    """Ritorna una versione compatta: solo nome prodotto e versione."""
    return f"{__product__} v{__version__}"
