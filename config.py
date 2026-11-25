
# tomllib ist das Python-Modul zum Einlesen von TOML-Konfigurationsdateien.
# Es ist ab Python 3.11 bereits Bestandteil von Python.
import tomllib

# Path erleichtert den Umgang mit Datei- und Verzeichnispfaden.
# Es funktioniert auch mit Windows-Pfaden.
from pathlib import Path


# Ermittelt das Verzeichnis, in dem sich diese config.py befindet.
# resolve() sorgt dafür, dass wir einen absoluten Pfad erhalten.
PROJECT_DIR = Path(__file__).resolve().parent

# Legt fest, wo unsere persönliche Konfigurationsdatei liegt.
# Sie befindet sich direkt im Hauptverzeichnis des Projekts.
CONFIG_PATH = PROJECT_DIR / "config.toml"


def load_config():
    """
    Lädt die Konfiguration aus der config.toml und überprüft deren Inhalt.

    Relative Pfade werden dabei automatisch in absolute Pfade umgewandelt.
    Die Funktion gibt anschließend die geladene Konfiguration zurück.
    """

    # Prüft zuerst, ob die Konfigurationsdatei überhaupt vorhanden ist.
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Konfigurationsdatei nicht gefunden: {CONFIG_PATH}"
        )

    # Öffnet die TOML-Datei im Binärmodus ("rb").
    # tomllib benötigt diesen Modus zum Einlesen der Datei.
    with CONFIG_PATH.open("rb") as file:

        # Liest den Inhalt der Datei und wandelt ihn
        # in eine Python-Datenstruktur (Dictionary) um.
        config = tomllib.load(file)

    # Holt die allgemeinen Einstellungen aus der Konfiguration.
    # Fehlt der Bereich, wird ein leeres Dictionary verwendet.
    settings = config.get("settings", {})

    # Prüft, ob der Einstellungsbereich gültig ist.
    if not isinstance(settings, dict):
        raise ValueError(
            "Der Bereich 'settings' muss ein gültiger Abschnitt sein."
        )

    # Prüft den Schalter für die Anzeige der Tools.
    # Standardmäßig werden die Tools nicht angezeigt.
    show_tools = settings.get("show_tools", False)

    # Prüft, ob tatsächlich true oder false angegeben wurde.
    if not isinstance(show_tools, bool):
        raise ValueError(
            "Ungültiger Wert für 'show_tools'. "
            "Erlaubt sind nur true oder false."
        )

    # Speichert den geprüften Wert.
    settings["show_tools"] = show_tools

    # Speichert die Einstellungen zurück in der Gesamtkonfiguration.
    config["settings"] = settings

    # Holt alle konfigurierten Skripte aus der Konfiguration.
    scripts = config.get("scripts")

    # Prüft, ob der Eintrag "scripts" vorhanden und eine Liste ist.
    if not isinstance(scripts, list):
        raise ValueError(
            "Die Konfiguration muss mindestens einen "
            "gültigen 'scripts'-Bereich enthalten."
        )

    # Geht alle konfigurierten Skripte einzeln durch.
    for index, script in enumerate(scripts, start=1):

        # Jeder Skripteintrag muss ein Dictionary sein.
        if not isinstance(script, dict):
            raise ValueError(
                f"Skript {index} ist kein gültiger Eintrag."
            )

        # Prüft, ob das Skript einen Namen besitzt.
        if not script.get("name"):
            raise ValueError(
                f"Skript {index} hat keinen Namen."
            )

        # Prüft, ob ein Dateipfad angegeben wurde.
        if not script.get("path"):
            raise ValueError(
                f"Skript '{script['name']}' hat keinen Pfad."
            )

        # Wandelt den angegebenen Pfad in ein Path-Objekt um.
        script_path = Path(script["path"])

        # Prüft, ob der angegebene Pfad bereits absolut ist.
        if not script_path.is_absolute():

            # Relative Pfade werden auf das Projektverzeichnis bezogen.
            script_path = PROJECT_DIR / script_path

        # Löst den Pfad vollständig auf und speichert ihn zurück.
        script["path"] = script_path.resolve()

        # Prüft den optionalen Parameter allow_manual_stop.
        # Wenn er fehlt, wird standardmäßig False verwendet.
        allow_manual_stop = script.get("allow_manual_stop", False)

        # Prüft, ob der Parameter tatsächlich einen Boolean enthält.
        if not isinstance(allow_manual_stop, bool):
            raise ValueError(
                f"Ungültiger Wert für allow_manual_stop bei Skript '{script['name']}'. "
                "Erlaubt sind nur true oder false."
            )

        # Speichert den geprüften Wert im Skripteintrag.
        script["allow_manual_stop"] = allow_manual_stop

    # Holt alle konfigurierten Tools aus der Konfiguration.
    # Wenn keine Tools vorhanden sind, wird eine leere Liste verwendet.
    tools = config.get("tools", [])

    # Prüft, ob der Eintrag eine Liste ist.
    if not isinstance(tools, list):
        raise ValueError(
            "Der Bereich 'tools' muss eine gültige Liste enthalten."
        )

    # Geht alle konfigurierten Tools einzeln durch.
    for index, tool in enumerate(tools, start=1):

        # Jeder Tool-Eintrag muss ein Dictionary sein.
        if not isinstance(tool, dict):
            raise ValueError(
                f"Tool {index} ist kein gültiger Eintrag."
            )

        # Prüft, ob das Tool einen Namen besitzt.
        if not tool.get("name"):
            raise ValueError(
                f"Tool {index} hat keinen Namen."
            )

        # Prüft, ob ein Dateipfad angegeben wurde.
        if not tool.get("path"):
            raise ValueError(
                f"Tool '{tool['name']}' hat keinen Pfad."
            )

        # Wandelt den angegebenen Pfad in ein Path-Objekt um.
        tool_path = Path(tool["path"])

        # Prüft, ob der angegebene Pfad bereits absolut ist.
        if not tool_path.is_absolute():

            # Relative Pfade werden auf das Projektverzeichnis bezogen.
            tool_path = PROJECT_DIR / tool_path

        # Löst den Pfad vollständig auf und speichert ihn zurück.
        tool["path"] = tool_path.resolve()

        # Liest den optionalen Parameter allow_manual_stop.
        # Standardmäßig ist das manuelle Beenden nicht erlaubt.
        allow_manual_stop = tool.get("allow_manual_stop", False)

        # Prüft, ob der Parameter tatsächlich einen Boolean enthält.
        if not isinstance(allow_manual_stop, bool):
            raise ValueError(
                f"Ungültiger Wert für allow_manual_stop "
                f"bei Tool '{tool['name']}'. "
                "Erlaubt sind nur true oder false."
            )

        # Speichert den geprüften Wert im Tool-Eintrag.
        tool["allow_manual_stop"] = allow_manual_stop

    # Prüft, ob alle Skripte und Tools eindeutige Namen besitzen.
    # Die Prüfung berücksichtigt auch Groß- und Kleinschreibung.
    used_names = set()

    # Führt Skripte und Tools für die Namensprüfung zusammen.
    all_entries = scripts + tools

    # Prüft jeden Eintrag auf einen gültigen und eindeutigen Namen.
    for entry in all_entries:

        # Prüft zuerst den Datentyp des Namens.
        if not isinstance(entry["name"], str):
            raise ValueError(
                "Skript- und Tool-Namen müssen gültige Texte sein."
            )

        # Entfernt überflüssige Leerzeichen.
        name = entry["name"].strip()

        # Prüft, ob der Name nach dem Bereinigen noch Inhalt besitzt.
        if not name:
            raise ValueError(
                "Skript- und Tool-Namen dürfen nicht leer sein."
            )

        # Vereinheitlicht den Namen für den Vergleich.
        normalized_name = name.casefold()

        # Prüft, ob dieser Name bereits verwendet wird.
        if normalized_name in used_names:
            raise ValueError(
                f"Der Name '{name}' ist mehrfach vergeben. "
                "Skript- und Tool-Namen müssen eindeutig sein."
            )

        # Speichert den Namen für die weiteren Prüfungen.
        used_names.add(normalized_name)

        # Übernimmt den bereinigten Namen in die Konfiguration.
        entry["name"] = name

    # Speichert die geprüften Tools zurück in der Gesamtkonfiguration.
    config["tools"] = tools

    # Gibt die vollständige Konfiguration an den Aufrufer zurück.
    return config
