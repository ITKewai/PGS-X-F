# utils/paths.py
from __future__ import annotations

from pathlib import Path
import sys


def is_frozen() -> bool:
    """
    Verifica se l'applicazione è in esecuzione come eseguibile PyInstaller.

    PyInstaller imposta l'attributo `sys.frozen` e crea la cartella temporanea
    `sys._MEIPASS` quando l'app viene eseguita da un bundle.

    Returns:
        bool: True se il programma è in esecuzione come EXE PyInstaller,
        False se è in esecuzione in ambiente di sviluppo.
    """
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def exe_dir() -> Path:
    """
    Restituisce la cartella principale da cui risolvere i percorsi dell'app.

    In modalità frozen, restituisce la cartella in cui si trova l'eseguibile.
    In modalità sviluppo, restituisce la root del progetto, assumendo che questo
    file si trovi dentro una cartella `utils/`.

    Returns:
        Path: Percorso della cartella dell'eseguibile o della root del progetto.
    """
    return Path(sys.executable).parent if is_frozen() else Path(__file__).resolve().parent.parent


def resource_path(rel: str | Path) -> Path:
    """
    Costruisce il percorso assoluto a una risorsa inclusa nell'applicazione.

    Questa funzione va usata per file di sola lettura inclusi nel bundle,
    come template, immagini, file YAML predefiniti, icone o altre risorse.

    In modalità PyInstaller, il percorso viene risolto dentro `sys._MEIPASS`.
    In modalità sviluppo, viene risolto relativamente alla root del progetto.

    Args:
        rel (str | Path): Percorso relativo della risorsa.

    Returns:
        Path: Percorso assoluto alla risorsa richiesta.
    """
    rel = Path(rel)
    if is_frozen():
        return Path(sys._MEIPASS) / rel  # type: ignore[attr-defined]
    return exe_dir() / rel


def get_run_dir(prefer_cwd: bool = True) -> Path:
    """
    Restituisce la cartella di lavoro effettiva per file utente.

    Questa funzione serve per decidere dove leggere o scrivere file modificabili
    dall'utente, come configurazioni, log, cache o output.

    Args:
        prefer_cwd (bool): Se True, usa la cartella corrente da cui l'utente
            ha lanciato il programma. Se False, usa la cartella dell'eseguibile
            o della root del progetto.

    Returns:
        Path: Percorso della cartella di lavoro selezionata.
    """
    return Path.cwd() if prefer_cwd else exe_dir()


def ensure_dir(p: Path) -> Path:
    """
    Crea una cartella se non esiste già.

    La creazione è ricorsiva e sicura: se la cartella esiste già,
    non viene sollevato alcun errore.

    Args:
        p (Path): Percorso della cartella da creare.

    Returns:
        Path: Lo stesso percorso passato in input.
    """
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_config_path(filename: str = "config.yaml", prefer_cwd: bool = True) -> Path:
    """
    Restituisce il percorso del file di configurazione.

    Il file viene cercato o creato nella cartella di lavoro effettiva,
    determinata da `get_run_dir()`.

    Args:
        filename (str): Nome del file di configurazione.
            Default: "config.yaml".
        prefer_cwd (bool): Se True, usa la cartella corrente di lancio.
            Se False, usa la cartella dell'eseguibile o della root del progetto.

    Returns:
        Path: Percorso assoluto al file di configurazione.
    """
    return get_run_dir(prefer_cwd=prefer_cwd) / filename


def in_run_subdir(*parts: str, prefer_cwd: bool = True, create: bool = False) -> Path:
    """
    Costruisce un percorso dentro la cartella di lavoro effettiva.

    Utile per ottenere percorsi come `logs/`, `cache/`, `output/`
    o altre sottocartelle usate dall'applicazione.

    Args:
        *parts (str): Parti del percorso da concatenare alla run directory.
            Esempio: `("logs", "app.log")`.
        prefer_cwd (bool): Se True, usa la cartella corrente di lancio.
            Se False, usa la cartella dell'eseguibile o della root del progetto.
        create (bool): Se True, crea il percorso risultante come cartella.
            Usare solo quando il percorso finale rappresenta una directory.

    Returns:
        Path: Percorso assoluto costruito dentro la run directory.
    """
    p = get_run_dir(prefer_cwd=prefer_cwd).joinpath(*parts)
    return ensure_dir(p) if create else p