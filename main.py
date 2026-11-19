
# Importiert datetime, um Zeitstempel für unsere Log-Ausgaben zu erzeugen.
from datetime import datetime

# Importiert die benötigten Bestandteile von Textual.
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, RichLog, Static

# Importiert unsere Funktion zum Laden der Konfiguration.
from config import load_config


class PowerScriptApp(App):
    """Hauptklasse unserer terminalbasierten Anwendung."""

    # Name der Anwendung oben links.
    TITLE = "Power Script"

    # Zusatzinformation oben rechts.
    SUB_TITLE = "Script Manager"

    # Verwendet unsere externe CSS-Datei für das Layout.
    CSS_PATH = "style.tcss"

    # Definiert die Tastenkombination zum Beenden.
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear_log", "Clear log"),
    ]

    def __init__(self):
        """Initialisiert die Anwendung und lädt die Skriptkonfiguration."""

        # Initialisiert zunächst die übergeordnete Textual-App.
        super().__init__()

        # Lädt alle Skripte aus der config.toml.
        self.config = load_config()

        # Speichert die Skriptliste für den späteren Zugriff.
        self.scripts = self.config["scripts"]

    def build_menu_text(self) -> str:
        """Erstellt den Menütext anhand der konfigurierten Skripte."""

        # Hier sammeln wir die einzelnen Menüeinträge.
        lines = []

        # Geht alle Skripte durch und nummeriert sie ab 1.
        for number, script in enumerate(self.scripts, start=1):

            # Erstellt einen Menüeintrag mit Nummer und Skriptname.
            lines.append(f"{number}) {script['name']}")

        # Verbindet alle Einträge mit Zeilenumbrüchen.
        script_block = "\n".join(lines)

        # Baut den vollständigen Menütext zusammen.
        return (
            f"[b]Scripts[/b]\n\n{script_block}\n\n"
            "[b]Other[/b]\n\nC) Clear log\nQ) Quit"
        )

    def compose(self) -> ComposeResult:
        """Erstellt die sichtbaren Elemente der Anwendung."""

        # Zeichnet die obere Kopfzeile.
        yield Header()

        # Ordnet Menü und Log-Fenster horizontal nebeneinander an.
        with Horizontal():

            # Erstellt das Menü mit den dynamischen Skripteinträgen.
            yield Static(self.build_menu_text(), id="menu")

            # Erstellt das Log-Fenster für spätere Skriptausgaben.
            yield RichLog(id="log", markup=True)

        # Zeichnet die untere Fußzeile.
        yield Footer()

    def on_mount(self) -> None:
        """Wird aufgerufen, sobald die Oberfläche fertig aufgebaut ist."""

        # Setzt den Titel des Menürahmens.
        self.query_one("#menu").border_title = "Menu"

        # Setzt den Titel des Lograhmens.
        self.query_one("#log").border_title = "Log"

        # Schreibt eine Startmeldung in das Log.
        self.write_log("SYSTEM", "Initialization finished")

    def write_log(self, source: str, message: str) -> None:
        """Schreibt eine formatierte Nachricht in das Log-Fenster."""

        # Ermittelt die aktuelle Uhrzeit.
        time = datetime.now().strftime("%H:%M:%S")

        # Erstellt eine formatierte Logzeile.
        line = f"[dim]{time}[/dim] | [cyan]{source:<8}[/cyan] | {message}"

        # Schreibt die Zeile in das sichtbare Log-Fenster.
        self.query_one("#log", RichLog).write(line)

    def action_clear_log(self) -> None:
        """Leert das Log-Fenster."""

        # Entfernt alle bisherigen Logeinträge.
        self.query_one("#log", RichLog).clear()

    def on_key(self, event) -> None:
        """Verarbeitet Tastatureingaben für die Skriptauswahl."""

        # Prüft, ob eine Ziffer zwischen 1 und 9 gedrückt wurde.
        if event.key in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):

            # Wandelt die gedrückte Taste in eine Zahl um.
            number = int(event.key)

            # Prüft, ob ein Skript mit dieser Nummer existiert.
            if number <= len(self.scripts):

                # Holt das passende Skript aus der Liste.
                script = self.scripts[number - 1]

                # Gibt vorerst nur eine Testmeldung aus.
                self.write_log(
                    "SCRIPT",
                    f"{script['name']} wurde ausgewählt."
                )

            # Verhindert, dass die Ziffer zusätzlich verarbeitet wird.
            event.stop()


# Startet die Anwendung, wenn diese Datei direkt ausgeführt wird.
if __name__ == "__main__":
    PowerScriptApp().run()