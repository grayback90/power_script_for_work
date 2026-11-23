
# Importiert datetime für die Zeitstempel im Log.
from datetime import datetime

# Importiert die benötigten Bestandteile von Textual.
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
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

        # Ordnet jede Eingabezeile dem zugehörigen Skriptnamen zu.
        self.script_input_names = {}

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

    def build_script_button_label(self, number: int, script: dict) -> str:
        """Erstellt die Beschriftung eines Skript-Buttons."""

        # Liest den aktuellen Status des Skripts.
        status = self.script_status[script["name"]]

        # Gibt Nummer, Namen und Status zurück.
        return f"{number}) {script['name']} - {status}"


    def refresh_menu(self) -> None:
        """Aktualisiert die Beschriftungen aller Skript-Buttons."""

        # Geht alle konfigurierten Skripte durch.
        for number, script in enumerate(self.scripts, start=1):

            # Ermittelt den passenden Button.
            button = self.query_one(
                f"#script-button-{number}",
                Button,
            )

            # Erstellt die neue Beschriftung.
            label = self.build_script_button_label(
                number,
                script,
            )

            # Setzt die neue Beschriftung.
            button.label = label

            # Erzwingt die Aktualisierung der Darstellung und Größe.
            button.refresh(layout=True)

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

            # Erstellt das Menü mit den Skript-Buttons.
            with Vertical(id="menu"):

                # Überschrift des Menüs.
                yield Static("[b]Scripts[/b]")

                # Erstellt für jedes konfigurierte Skript einen Button.
                for number, script in enumerate(self.scripts, start=1):

                    yield Button(
                        self.build_script_button_label(number, script),
                        id=f"script-button-{number}",
                    )

                # Bereich für weitere Funktionen.
                yield Static("[b]Other[/b]")

                # Button zum Leeren des System-Logs.
                yield Button(
                    "Clear system log",
                    id="clear-log-button",
                )

                # Button zum Beenden der Anwendung.
                yield Button(
                    "Quit",
                    id="quit-button",
                )

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
        self.query_one("#menu", Vertical).border_title = "Menu"

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

        # Erstellt das Log-Fenster für die Skriptausgaben.
        script_log = RichLog(
            id=log_id,
            markup=True,
            classes="script-log",
        )

        # Erstellt eine eindeutige ID für die Eingabezeile.
        input_id = f"script-input-{tab_number}"

        # Erstellt die Eingabezeile unterhalb des Logs.
        script_input = Input(
            id=input_id,
            placeholder="Eingabe für das Skript ...",
            classes="script-input",
        )

        # Merkt sich, zu welchem Skript diese Eingabe gehört.
        self.script_input_names[input_id] = name

        # Gruppiert Log und Eingabezeile in einem gemeinsamen Bereich.
        script_content = Vertical(
            script_log,
            script_input,
        )

        # Erstellt den neuen Tab mit dem gemeinsamen Inhaltsbereich.
        new_tab = TabPane(name, script_content, id=tab_id)
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
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Verarbeitet Klicks auf die Menü-Buttons."""

        # Ermittelt die ID des angeklickten Buttons.
        button_id = event.button.id

        # Prüft, ob ein Skript-Button angeklickt wurde.
        if button_id and button_id.startswith("script-button-"):

            # Ermittelt die Nummer aus der Button-ID.
            number = int(button_id.replace("script-button-", ""))

            # Holt das zugehörige Skript aus der Konfiguration.
            script = self.scripts[number - 1]

            # Startet das Skript über dieselbe Methode wie die Zahlentasten.
            self.run_worker(self.start_script_with_tab(script))

        # Prüft, ob der Button zum Leeren des System-Logs angeklickt wurde.
        elif button_id == "clear-log-button":

            self.action_clear_log()

        # Prüft, ob der Beenden-Button angeklickt wurde.
        elif button_id == "quit-button":

            self.exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Sendet eine Eingabe an den passenden Hintergrundprozess."""

        # Ermittelt anhand der ID, zu welchem Skript die Eingabe gehört.
        script_name = self.script_input_names.get(event.input.id)

        # Ohne Zuordnung kann die Eingabe nicht verarbeitet werden.
        if script_name is None:
            return

        # Holt den zugehörigen Prozess.
        process = self.script_manager.processes.get(script_name)

        # Prüft, ob der Prozess noch läuft und Eingaben annehmen kann.
        if process is None or process.poll() is not None:
            self.write_log(
                "ERROR",
                f"{script_name}: Prozess läuft nicht mehr."
            )
            event.input.value = ""
            return

        try:
            # Sendet den eingegebenen Text samt Zeilenumbruch.
            # Der Zeilenumbruch entspricht dem Drücken der Enter-Taste.
            process.stdin.write(event.value + "\n")

            # Stellt sicher, dass die Eingabe sofort übertragen wird.
            process.stdin.flush()

            # Zeigt die gesendete Eingabe im Skript-Log an.
            self.write_log(
                script_name,
                f"> {event.value}"
            )

            # Nach einer Eingabe kann das Skript weiterlaufen.
            self.set_script_status(script_name, "RUNNING")

        except (OSError, ValueError) as error:
            # Meldet Probleme beim Übertragen der Eingabe.
            self.write_log(
                "ERROR",
                f"{script_name}: Eingabe fehlgeschlagen: {error}"
            )

        finally:
            # Leert die Eingabezeile für die nächste Eingabe.
            event.input.value = ""

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

                # Entfernt den Tab nach dem Prozessende.
                # run_worker führt die asynchrone Methode aus,
                # ohne die Benutzeroberfläche zu blockieren.
                self.run_worker(self.remove_script_tab(name))

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

    async def remove_script_tab(self, name: str) -> None:
        """Entfernt den Tab und alle zugehörigen Daten eines Skripts."""

        # Ermittelt die ID des Tabs anhand des Skriptnamens.
        tab_id = self.script_tab_ids.get(name)

        # Falls kein Tab existiert, gibt es nichts zu entfernen.
        if tab_id is None:
            return

        # Entfernt den Tab anhand seiner ID aus der Oberfläche.
        await self.tabs.remove_pane(tab_id)

        # Entfernt die gespeicherte Log-Zuordnung.
        self.script_logs.pop(name, None)

        # Entfernt die gespeicherte Tab-ID.
        self.script_tab_ids.pop(name, None)

        # Sucht alle Eingabezeilen, die zu diesem Skript gehören.
        input_ids = [
            input_id
            for input_id, script_name in self.script_input_names.items()
            if script_name == name
        ]

        # Entfernt auch diese Eingabezeilen-Zuordnungen.
        for input_id in input_ids:
            self.script_input_names.pop(input_id, None)

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
