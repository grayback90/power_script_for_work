
# Importiert datetime für die Zeitstempel im Log.
from datetime import datetime

# Importiert die benötigten Bestandteile von Textual.
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, RichLog, Static

# Importiert unsere Konfigurationsverwaltung.
from config import load_config

# Importiert die neue Skriptverwaltung.
from core.script_manager import ScriptManager


class PowerScriptApp(App):
    """Hauptklasse unserer terminalbasierten Anwendung."""

    # Name der Anwendung oben links.
    TITLE = "Power Script"

    # Zusatzinformation oben rechts.
    SUB_TITLE = "Script Manager"

    # Verwendet unsere externe CSS-Datei.
    CSS_PATH = "style.tcss"

    # Tastenkombinationen der Anwendung.
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear_log", "Clear log"),
    ]

    def __init__(self):
        """Initialisiert die Anwendung."""

        # Initialisiert zuerst die Textual-App.
        super().__init__()

        # Lädt die Konfiguration.
        self.config = load_config()

        # Speichert die konfigurierten Skripte.
        self.scripts = self.config["scripts"]

        # Erstellt die Verwaltung für unsere Hintergrundprozesse.
        self.script_manager = ScriptManager()

    def build_menu_text(self) -> str:
        """Erstellt das Menü anhand der Konfiguration."""

        # Hier sammeln wir die Menüeinträge.
        lines = []

        # Geht alle Skripte durch und nummeriert sie.
        for number, script in enumerate(self.scripts, start=1):
            lines.append(f"{number}) {script['name']}")

        # Verbindet alle Einträge zu einem Text.
        script_block = "\n".join(lines)

        # Erstellt den vollständigen Menütext.
        return (
            f"[b]Scripts[/b]\n\n{script_block}\n\n"
            "[b]Other[/b]\n\nC) Clear log\nQ) Quit"
        )

    def compose(self) -> ComposeResult:
        """Erstellt die sichtbaren Elemente der Anwendung."""

        # Erstellt die Kopfzeile.
        yield Header()

        # Ordnet Menü und Log nebeneinander an.
        with Horizontal():

            # Erstellt das dynamische Menü.
            yield Static(self.build_menu_text(), id="menu")

            # Erstellt das Log-Fenster.
            yield RichLog(id="log", markup=True)

        # Erstellt die Fußzeile.
        yield Footer()

    def on_mount(self) -> None:
        """Wird nach dem Aufbau der Oberfläche ausgeführt."""

        # Setzt den Rahmen-Titel des Menüs.
        self.query_one("#menu").border_title = "Menu"

        # Setzt den Rahmen-Titel des Logs.
        self.query_one("#log").border_title = "Log"

        # Schreibt eine Startmeldung.
        self.write_log("SYSTEM", "Initialization finished")

        # Prüft alle 0,1 Sekunden auf neue Prozessmeldungen.
        self.set_interval(0.1, self.check_process_messages)

    def write_log(self, source: str, message: str) -> None:
        """Schreibt eine formatierte Nachricht ins Log."""

        # Ermittelt die aktuelle Uhrzeit.
        time = datetime.now().strftime("%H:%M:%S")

        # Erstellt die formatierte Logzeile.
        line = f"[dim]{time}[/dim] | [cyan]{source:<8}[/cyan] | {message}"

        # Schreibt die Nachricht in das Log-Fenster.
        self.query_one("#log", RichLog).write(line)

    def check_process_messages(self) -> None:
        """Holt neue Nachrichten aus der Prozessverwaltung ab."""

        # Fragt alle aktuell verfügbaren Nachrichten ab.
        messages = self.script_manager.get_messages()

        # Verarbeitet jede Nachricht einzeln.
        for message_type, name, message in messages:

            # Normale Skriptausgabe.
            if message_type == "output":
                self.write_log(name, message)

            # Erfolgreicher Start eines Skripts.
            elif message_type == "started":
                self.write_log("SYSTEM", f"{name}: {message}")

            # Prozess wurde beendet.
            elif message_type == "finished":
                self.write_log("SYSTEM", f"{name}: {message}")

            # Fehler beim Starten oder Ausführen.
            elif message_type == "error":
                self.write_log("ERROR", f"{name}: {message}")

    def action_clear_log(self) -> None:
        """Leert das Log-Fenster."""

        # Entfernt alle bisherigen Logeinträge.
        self.query_one("#log", RichLog).clear()

    def on_key(self, event) -> None:
        """Verarbeitet die Tastatureingaben für die Skriptauswahl."""

        # Prüft, ob eine Ziffer zwischen 1 und 9 gedrückt wurde.
        if event.key in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):

            # Wandelt die gedrückte Taste in eine Zahl um.
            number = int(event.key)

            # Prüft, ob ein Skript mit dieser Nummer existiert.
            if number <= len(self.scripts):

                # Holt das ausgewählte Skript.
                script = self.scripts[number - 1]

                # Liest den Namen und Pfad aus.
                script_name = script["name"]
                script_path = script["path"]

                # Übergibt das Skript an unsere Prozessverwaltung.
                self.script_manager.start_script(
                    script_name,
                    script_path,
                )

            else:
                # Meldet eine ungültige Skriptnummer.
                self.write_log(
                    "ERROR",
                    f"Kein Skript mit Nummer {number} konfiguriert."
                )

            # Verhindert eine weitere Verarbeitung der Taste.
            event.stop()


# Startet die Anwendung, wenn main.py direkt ausgeführt wird.
if __name__ == "__main__":
    PowerScriptApp().run()
