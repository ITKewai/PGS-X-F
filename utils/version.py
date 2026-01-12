#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo che contiene le informazioni di versione e metadati del progetto PGS-X-FindIndex.
"""
import os
import re
from typing import List

from utils.exports.tia_constants import __version__ as pgs_version


__version__ = "1.0.3.5"
__author__ = "ITKewai"
__company__ = ""
__product__ = "PGS-X-FindIndex"
__copyright__ = f"Autore: {__author__} © 2025 {__company__}"


def get_version_info() -> str:
    """Ritorna una stringa formattata con le info di versione."""
    return f"{__product__} v{__version__} [PGS {pgs_version}]"


def short() -> str:
    """Ritorna una versione compatta: solo nome prodotto e versione."""
    return f"{__product__} v{__version__}"


def get_pgsx_version() -> list[int]:
    """Ritorna la versione come (major, minor, patch, build)."""
    return [int(part) for part in pgs_version.split('.')]
