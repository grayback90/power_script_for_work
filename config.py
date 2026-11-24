
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

    # Holt alle konfigurierten Skripte aus der Konfiguration.
    # get() liefert None zurück, wenn der Eintrag nicht existiert.
    scripts = config.get("scripts")

    # Prüft, ob der Eintrag "scripts" vorhanden und eine Liste ist.
    if not isinstance(scripts, list):
        raise ValueError(
            "Die Konfiguration muss mindestens einen "
            "gültigen 'scripts'-Bereich enthalten."
        )

    # Geht alle konfigurierten Skripte einzeln durch.
    # enumerate() liefert zusätzlich eine laufende Nummer.
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
        # Dadurch enthält die Konfiguration anschließend immer
        # einen absoluten Pfad, unabhängig von der ursprünglichen Eingabe.
        script["path"] = script_path.resolve()

        # Prüft, ob der optionale Parameter allow_manual_stop vorhanden ist.
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

    # Gibt die vollständige Konfiguration an den Aufrufer zurück.
    return config
