
# Importiert datetime für die Zeitstempel im Log.
from datetime import datetime

from rich.text import Text

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

        # Speichert die zusätzlich konfigurierten Tools.
        self.tools = self.config.get("tools", [])

        # Führt Skripte und Tools für die Prozessverwaltung zusammen.
        self.all_scripts = self.scripts + self.tools

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
        # Speichert den Status aller Skripte und Tools.
        self.script_status = {
            script["name"]: "AUS"
            for script in self.all_scripts
        }

    def build_script_button_label(self, script_name: str) -> Text:
        """Erstellt die Button-Beschriftung mit farbigem Statussymbol."""

        status = self.script_status.get(script_name, "AUS")

        # Weist jedem Status sein eigenes Symbol und seine Farbe zu.
        if status == "RUNNING":
            symbol = "[+]"
            color = "green"
        elif status == "WAITING":
            symbol = "[!]"
            color = "orange1"
        else:
            symbol = "[-]"
            color = "white"

        # Erstellt die Beschriftung mit getrennt formatiertem Symbol.
        label = Text()
        label.append("[", style="white")
        label.append(symbol[1], style=color)
        label.append("]", style="white")
        label.append(f" {script_name}")

        return label

    def refresh_menu(self) -> None:
        """Aktualisiert Beschriftung und Farbe aller Menü-Buttons."""

        # Legt die passende Button-Variante für jeden Status fest.
        status_variants = {
            "AUS": "default",
            "RUNNING": "success",
            "WAITING": "warning",
        }

        # Aktualisiert die Buttons der Skripte.
        for number, script in enumerate(self.scripts, start=1):
            self.update_menu_button(
                script,
                f"#script-button-{number}",
                status_variants,
            )

        # Aktualisiert die Buttons der Tools.
        for number, tool in enumerate(self.tools, start=1):
            self.update_menu_button(
                tool,
                f"#tool-button-{number}",
                status_variants,
            )

    def update_menu_button(
        self,
        item: dict,
        button_id: str,
        status_variants: dict,
    ) -> None:
        """Aktualisiert Beschriftung und Farbe eines Menü-Buttons."""

        # Ermittelt den passenden Button.
        button = self.query_one(button_id, Button)

        # Liest den aktuellen Status des Eintrags.
        status = self.script_status[item["name"]]

        # Erstellt die neue Beschriftung.
        label = self.build_script_button_label(item["name"])

        # Aktualisiert die Beschriftung.
        button.label = label

        # Ändert die Farbe entsprechend dem Status.
        button.variant = status_variants.get(status, "default")

        # Aktualisiert die Darstellung und Größe.
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

        # Liest die Einstellung für den zusätzlichen Menübereich.
        settings = self.config["settings"]
        show_tools = settings["show_tools"]

        # Ordnet den gesamten Menübereich und den Tab-Bereich nebeneinander an.
        with Horizontal():

            # Linker Bereich mit den Menüspalten und dem System-Bereich.
            with Vertical(id="menu-area"):

                # Obere Zeile mit Skripten und zusätzlichen Funktionen.
                with Horizontal():

                    # Linke Spalte: Skripte.
                    with Vertical(id="scripts-menu"):

                        # Erstellt für jedes konfigurierte Skript einen Button.
                        for number, script in enumerate(self.scripts, start=1):

                            yield Button(
                                self.build_script_button_label(script["name"]),
                                id=f"script-button-{number}",
                            )

                    # Rechte Spalte nur anzeigen, wenn Tools aktiviert sind.
                    if show_tools:

                        with Vertical(id="additional-menu"):

                            # Erstellt für jedes konfigurierte Tool einen eigenen Button.
                            for number, tool in enumerate(self.tools, start=1):

                                yield Button(
                                    self.build_script_button_label(tool["name"]),
                                    id=f"tool-button-{number}",
                                )

                # Unterer Bereich für allgemeine Systemfunktionen.
                with Vertical(id="system-menu"):

                    # Wenn Tools angezeigt werden,
                    # stehen die System-Buttons nebeneinander.
                    if show_tools:

                        with Horizontal():

                            yield Button(
                                "Clear system log",
                                id="clear-log-button",
                            )

                            yield Button(
                                "Quit",
                                id="quit-button",
                            )

                    # Wenn nur Skripte angezeigt werden,
                    # stehen die System-Buttons untereinander.
                    else:

                        yield Button(
                            "Clear system log",
                            id="clear-log-button",
                        )

                        yield Button(
                            "Quit",
                            id="quit-button",
                        )

            # Erstellt den Tab-Container rechts neben dem Menübereich.
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

        # Gibt dem System-Tab die erste Tab-Farbe.
        self.query_one("#--content-tab-system-tab").add_class("tab-color-blue")

        # Setzt den Rahmen-Titel der linken Spalte.
        self.query_one("#scripts-menu", Vertical).border_title = "Skripte"

        # Setzt den Rahmen-Titel des System-Bereichs.
        self.query_one("#system-menu", Vertical).border_title = "System"

        # Verleiht dem System-Bereich einen gelben Rahmen.
        self.query_one("#system-menu", Vertical).styles.border = ("round", "yellow")

        # Setzt den Rahmen-Titel der rechten Spalte, sofern sie existiert.
        if self.config["settings"]["show_tools"]:
            self.query_one("#additional-menu", Vertical).border_title = "Weiteres"

        # Setzt den Rahmen-Titel des System-Logs.
        self.query_one("#system-log").border_title = "System Log"

        # Schreibt eine Startmeldung.
        self.write_log("SYSTEM", "Initialization finished")

        # Gibt Warnungen zu fehlenden Skripten und Tools im System-Log aus.
        for warning in self.config.get("_warnings", []):
            self.write_log("ERROR", warning)

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

        # Weist dem Tab nach dem Einfügen seine Farbe zu.
        self.call_after_refresh(
            self.color_script_tab,
            tab_id,
            tab_number
        )

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

        # Legt die Farbe der Nachrichtenquelle fest.
        if source == "SYSTEM":
            source_style = "bold blue"
        elif source == "ERROR":
            source_style = "bold red"
        else:
            source_style = "bold cyan"

        # Erstellt den formatierten Kopf der Logzeile.
        line = Text()
        line.append(time, style="dim")
        line.append("  |  ", style="dim")
        line.append(f"{source:<8}", style=source_style)
        line.append(" | ", style="dim")

        # Wandelt ANSI-Farbsequenzen der Skriptausgabe
        # in Rich-Text um und hängt sie an die Logzeile an.
        line.append_text(Text.from_ansi(message))

        # Systemmeldungen und Fehler gehören in den System-Tab.
        if source in ("SYSTEM", "ERROR"):
            target_log = self.query_one("#system-log", RichLog)

        # Normale Ausgaben gehören in den jeweiligen Skript-Tab.
        else:
            target_log = self.script_logs.get(source)

        # Schreibt die Nachricht, sofern ein passendes Log existiert.
        if target_log is not None:
            target_log.write(line)

    def color_script_tab(self, tab_id: str, tab_number: int):
        """Weist dem Tab-Button abwechselnd eine Farbe zu."""

        # Ermittelt den Tab-Button des neu erstellten Tabs.
        tab_button = self.query_one(f"#--content-tab-{tab_id}")

        # Wechselt zwischen Blau und Türkis.
        if tab_number % 2 == 1:
            tab_button.add_class("tab-color-teal")
        else:
            tab_button.add_class("tab-color-blue")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Verarbeitet Klicks auf die Menü-Buttons."""

        # Ermittelt die ID des angeklickten Buttons.
        button_id = event.button.id

        # Prüft, ob ein Skript- oder Tool-Button angeklickt wurde.
        if button_id and (
            button_id.startswith("script-button-")
            or button_id.startswith("tool-button-")
        ):

            # Ermittelt, ob ein Skript oder ein Tool ausgewählt wurde.
            if button_id.startswith("script-button-"):

                # Ermittelt die Nummer des Skript-Buttons.
                number = int(button_id.replace("script-button-", ""))

                # Holt das zugehörige Skript aus der Konfiguration.
                script = self.scripts[number - 1]

            else:

                # Ermittelt die Nummer des Tool-Buttons.
                number = int(button_id.replace("tool-button-", ""))

                # Holt das zugehörige Tool aus der Konfiguration.
                script = self.tools[number - 1]

            # Liest den Namen des ausgewählten Skripts.
            script_name = script["name"]

            # Prüft, ob das Skript bereits gestartet wurde.
            process = self.script_manager.processes.get(script_name)

            # Prüft, ob der Prozess noch läuft.
            if process is not None and process.poll() is None:

                # Prüft, ob das manuelle Beenden erlaubt ist.
                if not script.get("allow_manual_stop", False):

                    # Wechselt zum bereits geöffneten Tab des Skripts.
                    tab_id = self.script_tab_ids.get(script_name)

                    if tab_id is not None:
                        self.tabs.active = tab_id

                    return

                # Beendet das Skript einschließlich seiner Unterprozesse.
                stopped = self.script_manager.stop_script(script_name)

                # Meldet, ob das Beenden erfolgreich angestoßen wurde.
                if stopped:
                    self.write_log(
                        "SYSTEM",
                        f"{script_name}: Manuelles Beenden angefordert."
                    )
                else:
                    self.write_log(
                        "ERROR",
                        f"{script_name}: Beenden fehlgeschlagen."
                    )

                return

            # Wenn das Skript nicht läuft, wird es wie bisher gestartet.
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

# Startet die Anwendung, wenn main.py direkt ausgeführt wird.
if __name__ == "__main__":
    PowerScriptApp().run()
