
# tomllib ist das Python-Modul zum Einlesen von TOML-Konfigurationsdateien.
import tomllib

# Path erleichtert den Umgang mit Datei- und Verzeichnispfaden.
from pathlib import Path


# Ermittelt das Verzeichnis, in dem sich diese config.py befindet.
PROJECT_DIR = Path(__file__).resolve().parent

# Legt fest, wo sich die persönliche Konfigurationsdatei befindet.
CONFIG_PATH = PROJECT_DIR / "config.toml"


def load_config():
    """
    Lädt die Konfiguration aus der config.toml und überprüft deren Inhalt.

    Relative Pfade werden automatisch in absolute Pfade umgewandelt.
    Fehlende Skripte und Tools werden gemeldet und übersprungen.
    """

    # Prüft, ob die Konfigurationsdatei vorhanden ist.
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Konfigurationsdatei nicht gefunden: {CONFIG_PATH}"
        )

    # Liest die TOML-Datei ein.
    with CONFIG_PATH.open("rb") as file:
        config = tomllib.load(file)

    # Hier sammeln wir Warnungen zu fehlenden Skripten und Tools.
    warnings = []

    # Holt die allgemeinen Einstellungen.
    settings = config.get("settings", {})

    if not isinstance(settings, dict):
        raise ValueError(
            "Der Bereich 'settings' muss ein gültiger Abschnitt sein."
        )

    # Prüft die Anzeige der zusätzlichen Tools.
    show_tools = settings.get("show_tools", False)

    if not isinstance(show_tools, bool):
        raise ValueError(
            "Ungültiger Wert für 'show_tools'. "
            "Erlaubt sind nur true oder false."
        )

    settings["show_tools"] = show_tools
    config["settings"] = settings

    # Holt die konfigurierten Skripte.
    scripts = config.get("scripts")

    if not isinstance(scripts, list):
        raise ValueError(
            "Die Konfiguration muss mindestens einen "
            "gültigen 'scripts'-Bereich enthalten."
        )

    # Prüft alle Skripteinträge.
    for index, script in enumerate(scripts, start=1):

        if not isinstance(script, dict):
            raise ValueError(
                f"Skript {index} ist kein gültiger Eintrag."
            )

        if not isinstance(script.get("name"), str) or not script["name"].strip():
            raise ValueError(
                f"Skript {index} hat keinen gültigen Namen."
            )

        if not script.get("path"):
            raise ValueError(
                f"Skript '{script['name']}' hat keinen Pfad."
            )

        # Wandelt den Pfad in ein Path-Objekt um.
        script_path = Path(script["path"])

        # Relative Pfade beziehen sich auf das Projektverzeichnis.
        if not script_path.is_absolute():
            script_path = PROJECT_DIR / script_path

        # Speichert den vollständig aufgelösten Pfad.
        script_path = script_path.resolve()
        script["path"] = script_path

        # Prüft, ob die Datei existiert und eine Datei ist.
        if not script_path.exists():
            script["_path_valid"] = False
            warnings.append(
                f"Skript '{script['name']}' wurde nicht gefunden: {script_path}"
            )
        elif not script_path.is_file():
            script["_path_valid"] = False
            warnings.append(
                f"Der Pfad von Skript '{script['name']}' ist keine Datei: {script_path}"
            )
        else:
            script["_path_valid"] = True

        # Prüft den optionalen Parameter allow_manual_stop.
        allow_manual_stop = script.get("allow_manual_stop", False)

        if not isinstance(allow_manual_stop, bool):
            raise ValueError(
                f"Ungültiger Wert für allow_manual_stop bei Skript '{script['name']}'. "
                "Erlaubt sind nur true oder false."
            )

        script["allow_manual_stop"] = allow_manual_stop

    # Holt die konfigurierten Tools.
    tools = config.get("tools", [])

    if not isinstance(tools, list):
        raise ValueError(
            "Der Bereich 'tools' muss eine gültige Liste enthalten."
        )

    # Prüft alle Tool-Einträge.
    for index, tool in enumerate(tools, start=1):

        if not isinstance(tool, dict):
            raise ValueError(
                f"Tool {index} ist kein gültiger Eintrag."
            )

        if not isinstance(tool.get("name"), str) or not tool["name"].strip():
            raise ValueError(
                f"Tool {index} hat keinen gültigen Namen."
            )

        if not tool.get("path"):
            raise ValueError(
                f"Tool '{tool['name']}' hat keinen Pfad."
            )

        # Wandelt den Pfad in ein Path-Objekt um.
        tool_path = Path(tool["path"])

        # Relative Pfade beziehen sich auf das Projektverzeichnis.
        if not tool_path.is_absolute():
            tool_path = PROJECT_DIR / tool_path

        # Speichert den vollständig aufgelösten Pfad.
        tool_path = tool_path.resolve()
        tool["path"] = tool_path

        # Prüft, ob die Datei existiert und eine Datei ist.
        if not tool_path.exists():
            tool["_path_valid"] = False
            warnings.append(
                f"Tool '{tool['name']}' wurde nicht gefunden: {tool_path}"
            )
        elif not tool_path.is_file():
            tool["_path_valid"] = False
            warnings.append(
                f"Der Pfad von Tool '{tool['name']}' ist keine Datei: {tool_path}"
            )
        else:
            tool["_path_valid"] = True

        # Prüft den optionalen Parameter allow_manual_stop.
        allow_manual_stop = tool.get("allow_manual_stop", False)

        if not isinstance(allow_manual_stop, bool):
            raise ValueError(
                f"Ungültiger Wert für allow_manual_stop "
                f"bei Tool '{tool['name']}'. "
                "Erlaubt sind nur true oder false."
            )

        tool["allow_manual_stop"] = allow_manual_stop

    # Prüft, ob alle Skripte und Tools eindeutige Namen besitzen.
    used_names = set()

    all_entries = scripts + tools

    for entry in all_entries:

        if not isinstance(entry["name"], str):
            raise ValueError(
                "Skript- und Tool-Namen müssen gültige Texte sein."
            )

        name = entry["name"].strip()

        if not name:
            raise ValueError(
                "Skript- und Tool-Namen dürfen nicht leer sein."
            )

        normalized_name = name.casefold()

        if normalized_name in used_names:
            raise ValueError(
                f"Der Name '{name}' ist mehrfach vergeben. "
                "Skript- und Tool-Namen müssen eindeutig sein."
            )

        used_names.add(normalized_name)
        entry["name"] = name

    # Entfernt Einträge mit ungültigen Dateipfaden aus den Menüs.
    # Die Warnungen bleiben für das System-Log erhalten.
    config["scripts"] = [
        script for script in scripts
        if script["_path_valid"]
    ]

    config["tools"] = [
        tool for tool in tools
        if tool["_path_valid"]
    ]

    # Speichert die gesammelten Warnungen für die Anwendung.
    config["_warnings"] = warnings

    return config
