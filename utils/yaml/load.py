#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo per caricare, sanificare e normalizzare il file YAML di configurazione.

Il modulo gestisce file YAML che possono contenere piccole irregolarità sintattiche,
come liste flow-style con elementi vuoti o virgole finali. Dopo il caricamento,
normalizza alcune sezioni note della configurazione, in particolare `io` e `obj`,
raggruppandole in strutture più comode da usare nel resto dell'applicazione.
"""

import logging
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional


def _sanitize_yaml_like(text: str) -> str:
    """
    Sanifica alcune liste YAML flow-style contenenti elementi vuoti.

    Converte elementi mancanti all'interno di liste YAML in valori `null`,
    così da permettere a `yaml.safe_load()` di interpretarle correttamente.

    Esempi:
        [a, b,,]   -> [a, b, null, null]
        [,a,,b,]   -> [null, a, null, b, null]

    Args:
        text (str): Testo YAML originale da sanificare.

    Returns:
        str: Testo YAML modificato con elementi vuoti sostituiti da `null`.

    Notes:
        L'approccio è best-effort e basato su regex. È pensato per correggere
        casi reali e limitati del file di configurazione, non per sostituire
        un parser YAML completo.
    """
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r',\s*,', ', null,', text)  # elemento vuoto tra due virgole

    text = re.sub(r'\[\s*,', '[ null,', text)  # vuoto subito dopo '['
    text = re.sub(r'\[\s*,', '[ null,', text)  # vuoto subito dopo '['
    text = re.sub(r',\s*\]', ', null]', text)  # vuoto prima di ']'

    return text


def _sanitize_pstring_flow_lists(text: str) -> str:
    """
    Sanifica esclusivamente le righe `pstring` in formato lista flow-style.

    Converte righe del tipo:

        pstring: [a,b,,]

    in una forma più sicura per il parsing YAML:

        pstring: [a, b, null, null]

    Gli elementi vuoti, `none` e `null` vengono convertiti in `null`.
    Gli elementi contenenti spazi vengono quotati se non lo sono già.

    Args:
        text (str): Testo YAML da sanificare.

    Returns:
        str: Testo YAML con le sole liste `pstring` normalizzate.

    Notes:
        La funzione modifica solo righe che iniziano con `pstring: [...]`,
        preservando il resto del contenuto.
    """

    def fix(match: re.Match) -> str:
        """
        Converte una singola riga `pstring` trovata dalla regex.

        Args:
            match (re.Match): Match regex contenente indentazione e contenuto
                interno della lista `pstring`.

        Returns:
            str: Riga `pstring` ricostruita in forma normalizzata.
        """
        indent = match.group(1) or ""
        inner = match.group(2) or ""
        tokens = [t.strip() for t in inner.split(",")]
        out = []

        for t in tokens:
            if t == "" or t.lower() in {"none", "null"}:
                out.append("null")
            else:
                if not (t.startswith("'") and t.endswith("'")) and not (t.startswith('"') and t.endswith('"')):
                    if " " in t:
                        t = "'" + t.replace("'", "''") + "'"
                out.append(t)

        return f"{indent}pstring: [{', '.join(out)}]"

    return re.sub(r"(?mi)^(\s*)pstring\s*:\s*\[(.*?)\]\s*$", fix, text)


def _is_row(x: Any) -> bool:
    """
    Verifica se un valore rappresenta una riga semplice.

    Una riga semplice è una lista che non contiene altre liste o dizionari.
    Viene usata per distinguere righe dati da strutture annidate.

    Args:
        x (Any): Valore da verificare.

    Returns:
        bool: True se `x` è una lista piatta, False altrimenti.
    """
    return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)


def _group_io(io_node: Any, keys: tuple[str, ...] = ('di', 'ai', 'do', 'ao', 'ri', 'fb')) -> Dict[str, List[list]]:
    """
    Raggruppa la sezione `io` della configurazione per tipologia di segnale.

    Gestisce sia configurazioni in forma lista sia in forma dizionario.
    Le chiavi riconosciute vengono normalizzate in minuscolo e aggregate
    in un dizionario con liste di righe.

    Args:
        io_node (Any): Nodo YAML relativo alla sezione `io`.
        keys (tuple[str, ...]): Chiavi IO da riconoscere e includere nel risultato.
            Default: ('di', 'ai', 'do', 'ao', 'ri', 'fb').

    Returns:
        Dict[str, List[list]]: Dizionario con una lista di righe per ogni chiave IO.

    Example:
        Input YAML equivalente a:

            io:
              - di: [A, B, C]
              - ai:
                  - [X, Y]
                  - [Z, W]

        viene normalizzato in:

            {
                "di": [[A, B, C]],
                "ai": [[X, Y], [Z, W]],
                ...
            }
    """
    grouped: Dict[str, List[list]] = {k: [] for k in keys}

    if isinstance(io_node, list):
        for item in io_node:
            if isinstance(item, dict) and len(item) == 1:
                k, v = next(iter(item.items()))
                kl = str(k).lower()

                if kl in grouped:
                    if _is_row(v):
                        grouped[kl].append(v)
                    elif isinstance(v, list):
                        grouped[kl].extend([el for el in v if _is_row(el)])

    elif isinstance(io_node, dict):
        for k, v in io_node.items():
            kl = str(k).lower()

            if kl in grouped:
                if _is_row(v):
                    grouped[kl].append(v)
                elif isinstance(v, list):
                    grouped[kl].extend([el for el in v if _is_row(el)])

    return grouped


def _group_obj(obj_node: Any) -> Dict[str, List[list] | List[dict]]:
    """
    Raggruppa e normalizza la sezione `obj` della configurazione.

    La funzione attraversa ricorsivamente il nodo `obj` e raccoglie le righe
    associate alle chiavi note:

        - fb
        - input
        - output
        - mot
        - alarm
        - maint

    Inoltre preserva i blocchi `axis` completi, invece di appiattirli,
    perché possono contenere sottosezioni strutturate come `int`, `bool`
    e `type`.

    Args:
        obj_node (Any): Nodo YAML relativo alla sezione `obj`.

    Returns:
        Dict[str, List[list] | List[dict]]: Dizionario normalizzato contenente
        liste di righe per le sezioni semplici e lista di dizionari per `axis`.

    Example:
        Output tipico:

            {
                "fb": [...],
                "input": [...],
                "output": [...],
                "mot": [...],
                "alarm": [...],
                "maint": [...],
                "axis": [
                    {
                        "axis": [...],
                        "int": [...],
                        "bool": [...],
                        "type": [...]
                    }
                ]
            }
    """
    grouped: Dict[str, List[list] | List[dict]] = {
        'fb': [],
        'input': [],
        'output': [],
        'mot': [],
        'alarm': [],
        'axis': [],
        'maint': [],
    }

    def _is_row(x: Any) -> bool:
        """
        Verifica se un valore rappresenta una riga piatta della sezione `obj`.

        Args:
            x (Any): Valore da verificare.

        Returns:
            bool: True se `x` è una lista piatta, False altrimenti.
        """
        return isinstance(x, list) and all(not isinstance(e, (list, dict)) for e in x)

    def walk(node: Any) -> None:
        """
        Attraversa ricorsivamente il nodo `obj` e popola `grouped`.

        Args:
            node (Any): Nodo corrente da analizzare.

        Returns:
            None
        """
        if isinstance(node, dict):
            # Se è un blocco axis, lo conserviamo intero.
            if 'axis' in node and isinstance(node.get('axis'), list):
                grouped['axis'].append(node)

            for k, v in node.items():
                kl = str(k).lower()

                if kl in ('fb', 'input', 'output', 'mot', 'alarm', 'maint'):
                    if _is_row(v):
                        grouped[kl].append(v)
                    elif isinstance(v, list):
                        grouped[kl].extend([el for el in v if _is_row(el)])

                walk(v)

        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(obj_node)
    return grouped


def _pack_by_index(rows: List[list], idx_pos: int = 7) -> List[Optional[list]]:
    """
    Riorganizza una lista di righe usando un indice contenuto in ogni riga.

    Se una riga contiene un intero non negativo nella posizione `idx_pos`,
    viene inserita nella lista finale esattamente a quell'indice. Gli indici
    mancanti vengono riempiti con `None`.

    Le righe senza indice valido, con indice duplicato o con struttura non valida
    vengono aggiunte in fondo come extra.

    Args:
        rows (List[list]): Lista di righe da riorganizzare.
        idx_pos (int): Posizione dell'indice all'interno di ogni riga.
            Default: 7.

    Returns:
        List[Optional[list]]: Lista riorganizzata per indice, eventualmente
        contenente `None` nei buchi e righe extra in coda.

    Notes:
        Se nessuna riga contiene un indice valido, viene restituita la lista
        originale senza modifiche.
    """
    indexed: Dict[int, list] = {}
    extras: List[list] = []

    for r in rows:
        idx = r[idx_pos] if isinstance(r, list) and len(r) > idx_pos and isinstance(r[idx_pos], int) and r[idx_pos] >= 0 else None
        if idx is None:
            extras.append(r)
        elif idx not in indexed:
            indexed[idx] = r
        else:
            extras.append(r)

    if not indexed:
        return rows

    packed: List[Optional[list]] = [None] * (max(indexed.keys()) + 1)

    for i, r in indexed.items():
        packed[i] = r

    packed.extend(extras)
    return packed


def load_yaml(path: str) -> Any:
    """
    Carica, sanifica e normalizza un file YAML di configurazione.

    La funzione tenta prima di leggere il file YAML così com'è. Se il parsing
    fallisce, applica progressivamente alcune sanificazioni automatiche:

        1. `_sanitize_yaml_like()`
        2. `_sanitize_pstring_flow_lists()`

    Dopo il caricamento, normalizza le sezioni principali:

        - `io`: raggruppata tramite `_group_io()`
        - `obj`: raggruppata tramite `_group_obj()`

    Inoltre sostituisce con stringa vuota il primo elemento delle righe IO
    quando tale elemento è `None`.

    Args:
        path (str): Percorso del file YAML da caricare.

    Returns:
        Any: Struttura dati risultante dal parsing YAML, con sezioni `io`
        e `obj` normalizzate.

    Raises:
        RuntimeError: Se il file YAML non può essere caricato nemmeno dopo
        i tentativi di sanificazione.
        OSError: Se il file non esiste o non può essere letto.

    Notes:
        Il valore restituito è normalmente un dizionario, ma il tipo rimane
        `Any` perché dipende dal contenuto effettivo del file YAML.
    """
    logging.debug("📂 IN: load_yaml")

    text = Path(path).read_text(encoding='utf-8')

    try:
        data = yaml.safe_load(text)
        logging.debug(f"✅ YAML caricato correttamente al primo tentativo: {path}")

    except yaml.YAMLError:
        logging.debug("⚠️ YAML non valido al primo parsing: → applico _sanitize_yaml_like()")
        text2 = _sanitize_yaml_like(text)

        try:
            data = yaml.safe_load(text2)
            logging.debug(f"✅ YAML caricato dopo _sanitize_yaml_like(): {path}")

        except yaml.YAMLError as e1:
            logging.debug(f"⚠️ Ancora errore dopo _sanitize_yaml_like(): {e1} → applico _sanitize_pstring_flow_lists()")
            text3 = _sanitize_pstring_flow_lists(text2)

            try:
                data = yaml.safe_load(text3)
                logging.debug(f"✅ YAML caricato dopo _sanitize_pstring_flow_lists(): {path}")

            except yaml.YAMLError as e2:
                logging.error(f"❌ Impossibile leggere il file YAML '{path}' anche dopo le sanificazioni: {e2}")
                raise RuntimeError("Config YAML non leggibile dopo i tentativi di sanificazione.") from e2

    # ---- Raggruppa IO ----
    io_grouped = _group_io(data.get('io'))

    for key, arr in io_grouped.items():
        if isinstance(arr, list):
            for i, row in enumerate(arr):
                if isinstance(row, list) and row:
                    if row[0] is None:
                        row[0] = ""

    data['io'] = io_grouped

    # ---- Raggruppa OBJ ----
    data['obj'] = _group_obj(data.get('obj'))

    logging.debug("📂 OUT: load_yaml")
    return data
