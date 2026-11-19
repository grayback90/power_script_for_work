
# Importiert datetime für die Zeitstempel im Log.
from datetime import datetime

# Importiert die benötigten Bestandteile von Textual.
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import (
    Footer,
    Header,
    RichLog,
    Static,
    TabbedContent,
    TabPane,
)

# Importiert unsere Konfigurationsverwaltung.
from config import load_config

# Importiert die Verwaltung unserer Hintergrundprozesse.
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
        ("c", "clear_log", "Clear system log"),
    ]

    def __init__(self):
        """Initialisiert die Anwendung."""

        # Initialisiert zuerst die Textual-App.
        super().__init__()

        # Lädt die Konfiguration.
        self.config = load_config()

        # Speichert die konfigurierten Skripte.
        self.scripts = self.config["scripts"]

        # Erstellt die Verwaltung unserer Hintergrundprozesse.
        self.script_manager = ScriptManager()

        # Speichert die Log-Fenster der einzelnen Skripte.
        # Der Skriptname dient dabei als Schlüssel.
        self.script_logs = {}

        # Speichert die Tab-IDs anhand des Skriptnamens.
        self.script_tab_ids = {}

        # Zählt die Tabs, damit jeder eine eindeutige ID erhält.
        self.next_tab_number = 1

        # Wird später mit dem Tab-Container der Oberfläche verbunden.
        self.tabs = None

        # Speichert den aktuellen Status jedes konfigurierten Skripts.
        # Beim Programmstart ist zunächst jedes Skript ausgeschaltet.
        self.script_status = {
            script["name"]: "AUS"
            for script in self.scripts
        }

    def build_menu_text(self) -> str:
        """Erstellt das Menü anhand der Konfiguration und Statuswerte."""

        # Hier sammeln wir die Menüeinträge.
        lines = []

        # Geht alle Skripte durch und nummeriert sie.
        for number, script in enumerate(self.scripts, start=1):

            # Liest den aktuellen Status des Skripts.
            status = self.script_status[script["name"]]

            # Erstellt den Menüeintrag mit Name und Status.
            lines.append(
                f"{number}) {script['name']} - {status}"
            )

        # Verbindet alle Einträge zu einem Text.
        script_block = "\n".join(lines)

        # Erstellt den vollständigen Menütext.
        return (
            f"[b]Scripts[/b]\n\n{script_block}\n\n"
            "[b]Other[/b]\n\nC) Clear system log\nQ) Quit"
        )

    def refresh_menu(self) -> None:
        """Aktualisiert die Menüanzeige mit den aktuellen Statuswerten."""

        # Erstellt den Menütext neu und übergibt ihn an das sichtbare Element.
        self.query_one("#menu", Static).update(
            self.build_menu_text()
        )

    def set_script_status(self, name: str, status: str) -> None:
        """Ändert den Status eines Skripts und aktualisiert das Menü."""

        # Speichert den neuen Status.
        self.script_status[name] = status

        # Aktualisiert die sichtbare Menüanzeige.
        self.refresh_menu()

    def compose(self) -> ComposeResult:
        """Erstellt die sichtbaren Elemente der Anwendung."""

        # Erstellt die Kopfzeile.
        yield Header()

        # Ordnet Menü und Tab-Bereich nebeneinander an.
        with Horizontal():

            # Erstellt das dynamische Menü.
            yield Static(self.build_menu_text(), id="menu")

            # Erstellt den Tab-Container.
            with TabbedContent(id="script-tabs"):

                # Der System-Tab ist von Anfang an vorhanden.
                with TabPane("System", id="system-tab"):

                    # Hier erscheinen allgemeine Meldungen und Fehler.
                    yield RichLog(id="system-log", markup=True)

        # Erstellt die Fußzeile.
        yield Footer()

    def on_mount(self) -> None:
        """Wird nach dem Aufbau der Oberfläche ausgeführt."""

        # Verbindet unsere Variable mit dem Tab-Container.
        self.tabs = self.query_one("#script-tabs", TabbedContent)

        # Setzt den Rahmen-Titel des Menüs.
        self.query_one("#menu").border_title = "Menu"

        # Setzt den Rahmen-Titel des System-Logs.
        self.query_one("#system-log").border_title = "System Log"

        # Schreibt eine Startmeldung.
        self.write_log("SYSTEM", "Initialization finished")

        # Prüft alle 0,1 Sekunden auf neue Prozessmeldungen.
        self.set_interval(0.1, self.check_process_messages)

    async def create_script_tab(self, name: str) -> None:
        """Erstellt einen eigenen Tab für ein Skript."""

        # Prüft, ob für dieses Skript bereits ein Tab existiert.
        if name in self.script_logs:

            # Leert das alte Log, wenn das Skript erneut gestartet wird.
            self.script_logs[name].clear()

            # Aktiviert den bereits vorhandenen Tab.
            self.tabs.active = self.script_tab_ids[name]
            return

        # Erstellt eine eindeutige Nummer für den neuen Tab.
        tab_number = self.next_tab_number
        self.next_tab_number += 1

        # Erstellt eindeutige IDs für Tab und Log.
        tab_id = f"script-tab-{tab_number}"
        log_id = f"script-log-{tab_number}"

        # Erstellt das Log-Fenster für dieses Skript.
        script_log = RichLog(id=log_id, markup=True)

        # Erstellt einen neuen Tab und fügt ihn dem Tab-Container hinzu.
        new_tab = TabPane(name, script_log, id=tab_id)
        await self.tabs.add_pane(new_tab)

        # Speichert das Log-Fenster unter dem Skriptnamen.
        self.script_logs[name] = script_log

        # Speichert die zugehörige Tab-ID.
        self.script_tab_ids[name] = tab_id

        # Aktiviert den neu erstellten Tab.
        self.tabs.active = tab_id

    def write_log(self, source: str, message: str) -> None:
        """Schreibt eine formatierte Nachricht in das passende Log."""

        # Ermittelt die aktuelle Uhrzeit.
        time = datetime.now().strftime("%H:%M:%S")

        # Erstellt die formatierte Logzeile.
        line = f"[dim]{time}[/dim] | [cyan]{source:<8}[/cyan] | {message}"

        # Systemmeldungen und Fehler gehören in den System-Tab.
        if source in ("SYSTEM", "ERROR"):
            target_log = self.query_one("#system-log", RichLog)

        # Normale Ausgaben gehören in den jeweiligen Skript-Tab.
        else:
            target_log = self.script_logs.get(source)

        # Schreibt die Nachricht, sofern ein passendes Log existiert.
        if target_log is not None:
            target_log.write(line)

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

                # Setzt den Status auf RUNNING.
                self.set_script_status(name, "RUNNING")

                # Schreibt die Startmeldung in das System-Log.
                self.write_log("SYSTEM", f"{name}: {message}")

            # Skript wartet auf eine Eingabe, beispielsweise bei pause.
            elif message_type == "waiting":

                # Ändert den Status auf WAITING.
                self.set_script_status(name, "WAITING")

                # Schreibt die Meldung in das System-Log.
                self.write_log("SYSTEM", f"{name}: {message}")

            # Prozess wurde beendet.
            elif message_type == "finished":

                # Setzt den Status wieder auf AUS.
                self.set_script_status(name, "AUS")

                # Schreibt die Abschlussmeldung in das System-Log.
                self.write_log("SYSTEM", f"{name}: {message}")

            # Fehler beim Starten oder Ausführen.
            elif message_type == "error":

                # Bei einem Fehler bleibt das Skript auf AUS.
                self.set_script_status(name, "AUS")

                # Schreibt die Fehlermeldung in das System-Log.
                self.write_log("ERROR", f"{name}: {message}")

    def action_clear_log(self) -> None:
        """Leert das System-Log."""

        # Entfernt alle bisherigen Einträge im System-Tab.
        self.query_one("#system-log", RichLog).clear()

    async def start_script_with_tab(self, script: dict) -> None:
        """Erstellt den Tab und startet anschließend das Skript."""

        # Liest den Namen des ausgewählten Skripts.
        script_name = script["name"]

        # Prüft, ob das Skript bereits läuft.
        existing_process = self.script_manager.processes.get(script_name)

        if existing_process is not None:
            if existing_process.poll() is None:

                # Verhindert einen zweiten Start desselben Skripts.
                self.write_log(
                    "ERROR",
                    f"{script_name}: Skript läuft bereits."
                )
                return

        # Erstellt den Tab oder leert einen bereits vorhandenen Tab.
        await self.create_script_tab(script_name)

        # Übergibt das Skript an die Prozessverwaltung.
        self.script_manager.start_script(
            script_name,
            script["path"],
        )

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

                # Startet die Tab-Erstellung und den Skriptstart.
                # Die Anwendung bleibt währenddessen bedienbar.
                self.run_worker(self.start_script_with_tab(script))

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
