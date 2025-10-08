#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo che contiene le informazioni di versione e metadati del progetto PSG-X-FindIndex.
"""

__version__ = "1.0.3b"
__pgs_version__ = "0.25.42.0"
__author__ = "ITKewai"
__company__ = ""
__product__ = "PSG-X-FindIndex"
__copyright__ = f"Autore: {__author__} © 2025 {__company__}"


def get_version_info() -> str:
    """Ritorna una stringa formattata con le info di versione."""
    return (
        f"{__product__} v{__version__}\n"
        f"PGS config: {__pgs_version__}\n"
        f"{__copyright__}"
    )


def short() -> str:
    """Ritorna una versione compatta: solo nome prodotto e versione."""
    return f"{__product__} v{__version__}"
