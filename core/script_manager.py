
# subprocess ermöglicht es Python, externe Programme zu starten.
import subprocess

# threading ermöglicht das Auslesen der Prozessausgabe
# unabhängig von der Benutzeroberfläche.
import threading

# queue dient als sichere Nachrichtenübergabe zwischen Threads.
import queue

# Path wird für die Verarbeitung von Dateipfaden verwendet.
from pathlib import Path


class ScriptManager:
    """Verwaltet das Starten und Überwachen von CMD-/BAT-Skripten."""

    def __init__(self):
        """Initialisiert die Verwaltung."""

        # Hier speichern wir alle gestarteten Prozesse.
        # Der Name des Skripts dient als Schlüssel.
        self.processes = {}

        # In dieser Warteschlange sammeln wir die Ausgaben
        # und Statusmeldungen der Hintergrundprozesse.
        self.messages = queue.Queue()

    def start_script(self, name: str, path: Path):
        """Startet ein CMD-/BAT-Skript im Hintergrund."""

        # Prüft, ob die Datei tatsächlich existiert.
        if not path.is_file():
            self.messages.put(
                ("error", name, f"Datei nicht gefunden: {path}")
            )
            return

        # Verhindert, dass dasselbe Skript mehrfach gestartet wird.
        if name in self.processes:
            if self.processes[name].poll() is None:
                self.messages.put(
                    ("error", name, "Skript läuft bereits.")
                )
                return

        try:
            # Baut den Windows-Befehl zusammen.
            # Die Anführungszeichen schützen auch Pfade mit Leerzeichen.
            command = f'cmd.exe /d /c call "{path}"'

            # Startet CMD direkt mit dem vorbereiteten Befehlsstring.
            process = subprocess.Popen(
                command,

                # Fängt die normale Ausgabe des Skripts ab.
                stdout=subprocess.PIPE,

                # Leitet Fehlermeldungen ebenfalls in die Ausgabe.
                stderr=subprocess.STDOUT,

                # Ermöglicht später Eingaben für Befehle wie pause.
                stdin=subprocess.PIPE,

                # Wandelt die Ausgabe direkt in Text um.
                text=True,

                # Verwendet die Windows-Zeichenkodierung.
                encoding="mbcs",

                # Ersetzt nicht lesbare Zeichen.
                errors="replace",

                # Verhindert ein zusätzliches Konsolenfenster.
                creationflags=subprocess.CREATE_NO_WINDOW,

                # Keine zusätzliche Shell starten.
                shell=False,

                # Verwendet das Verzeichnis der gestarteten BAT-Datei
                # als Arbeitsverzeichnis.
                cwd=str(path.parent),
            )

            # Speichert den gestarteten Prozess.
            self.processes[name] = process

            # Meldet der Oberfläche, dass das Skript gestartet wurde.
            self.messages.put(
                ("started", name, "Skript wurde gestartet.")
            )

            # Startet einen eigenen Thread zum Auslesen der Ausgabe.
            reader = threading.Thread(
                target=self._read_output,
                args=(name, process),
                daemon=True,
            )

            # Startet den Hintergrund-Thread.
            reader.start()

        except OSError as error:
            # Fängt Fehler beim Starten des Prozesses ab.
            self.messages.put(
                ("error", name, f"Start fehlgeschlagen: {error}")
            )

    def _read_output(self, name: str, process):
        """Liest die Prozessausgabe und erkennt eine Pause."""

        # Sammelt die Zeichen der aktuell gelesenen Zeile.
        line_buffer = ""

        # Speichert einen kurzen Ausschnitt der letzten Ausgabe.
        recent_output = ""

        # Verhindert, dass WAITING mehrfach gemeldet wird.
        waiting_detected = False

        return_code = None

        try:
            # Liest die Ausgabe zeichenweise statt zeilenweise.
            while True:
                character = process.stdout.read(1)

                # Ein leerer String bedeutet, dass die Ausgabe beendet ist.
                if character == "":
                    break

                # Fügt das Zeichen zur aktuellen Zeile hinzu.
                line_buffer += character

                # Behält nur die letzten 120 Zeichen für die Erkennung.
                recent_output = (recent_output + character)[-120:]

                # Wandelt die Ausgabe für den Vergleich in Kleinbuchstaben um.
                normalized_output = recent_output.casefold()

                # Erkennt die typische Aufforderung des CMD-Pause-Befehls.
                pause_prompt = (
                    "press any key to continue" in normalized_output
                    or "beliebige taste" in normalized_output
                )

                # Prüft, ob gerade eine Pause erkannt wurde.
                if pause_prompt and not waiting_detected:

                    # Gibt die bisherige Ausgabe an die Oberfläche weiter.
                    prompt = line_buffer.strip()

                    if prompt:
                        self.messages.put(
                            ("output", name, prompt)
                        )

                    # Leert den Zeilenpuffer.
                    line_buffer = ""

                    # Merkt sich, dass die Pause bereits erkannt wurde.
                    waiting_detected = True

                    # Meldet der Oberfläche den neuen Status.
                    self.messages.put(
                        ("waiting", name, "Skript wartet auf eine Eingabe.")
                    )

                # Prüft, ob eine vollständige Zeile vorliegt.
                if character == "\n":

                    # Entfernt Zeilenumbrüche und überflüssige Leerzeichen.
                    line = line_buffer.rstrip()

                    # Übergibt die Zeile an die Oberfläche.
                    if line:
                        self.messages.put(
                            ("output", name, line)
                        )

                    # Bereitet die Puffer für die nächste Zeile vor.
                    line_buffer = ""
                    recent_output = ""

            # Gibt einen eventuell verbliebenen Text am Ende aus.
            remaining_text = line_buffer.rstrip()

            if remaining_text:
                self.messages.put(
                    ("output", name, remaining_text)
                )

        except OSError as error:
            # Meldet Probleme beim Lesen der Prozessausgabe.
            self.messages.put(
                ("error", name, f"Fehler beim Lesen: {error}")
            )

        finally:
            # Wartet auf das tatsächliche Ende des Prozesses.
            try:
                return_code = process.wait()

            except OSError as error:
                self.messages.put(
                    ("error", name, f"Fehler beim Warten auf Prozessende: {error}")
                )

            # Schließt die Eingabepipe.
            if process.stdin is not None:
                try:
                    process.stdin.close()
                except (OSError, ValueError):
                    pass

            # Schließt die Ausgabepipe.
            if process.stdout is not None:
                try:
                    process.stdout.close()
                except (OSError, ValueError):
                    pass

            # Entfernt den Prozess nur dann aus dem Register,
            # wenn dort noch genau dieser Prozess gespeichert ist.
            if self.processes.get(name) is process:
                self.processes.pop(name, None)

            # Meldet der Oberfläche das Prozessende.
            if return_code is not None:
                self.messages.put(
                    ("finished", name, f"Prozess beendet. Exit-Code: {return_code}")
                )

    def stop_script(self, name: str) -> bool:
        """Beendet ein freigegebenes Skript einschließlich seiner Unterprozesse."""

        # Holt den Prozess anhand des Skriptnamens.
        process = self.processes.get(name)

        # Prüft, ob das Skript überhaupt bekannt ist.
        if process is None:
            return False

        # Prüft, ob der Prozess noch läuft.
        if process.poll() is not None:
            return False

        try:
            # Beendet den gesamten Prozessbaum des gestarteten CMD-Prozesses.
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                check=True,
                capture_output=True,
                text=True,
            )

            return True

        except subprocess.CalledProcessError as error:
            # Meldet einen Fehler beim Beenden des Prozesses.
            self.messages.put(
                ("error", name, f"Beenden fehlgeschlagen: {error.stderr}")
            )
            return False

    def get_messages(self):
        """Liefert alle aktuell verfügbaren Nachrichten zurück."""

        # Sammelt alle Nachrichten, ohne auf neue warten zu müssen.
        collected = []

        # Holt Nachrichten einzeln ab, bis die Warteschlange leer ist.
        while True:
            try:
                collected.append(self.messages.get_nowait())

            except queue.Empty:
                break

        return collected
