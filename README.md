# Power Script

Eine zentrale, terminalbasierte Oberfläche zum Starten und Überwachen von Windows-CMD-Skripten.

## 📖 Projektbeschreibung

Im Arbeitsalltag kommen häufig verschiedene Skripte zum Einsatz, beispielsweise zum Starten und Stoppen von Entwicklungsumgebungen, zum Ausführen von Wartungsaufgaben oder zum Vorbereiten lokaler Testumgebungen.

**Power Script** soll diese Skripte über eine gemeinsame Oberfläche zugänglich machen.

Anstatt mehrere CMD-Fenster manuell zu öffnen und deren Ausgaben separat zu verfolgen, werden die Skripte direkt über eine zentrale Terminal-Oberfläche gestartet. Die jeweiligen Ausgaben erscheinen in eigenen Tabs.

Das Projekt wird mit Python entwickelt. Die eigentlichen Arbeitsskripte bleiben eigenständige CMD- bzw. BAT-Dateien.

## 🎯 Geplante Funktionen

- **Zentrales Menü:** Alle konfigurierten Skripte werden automatisch in einer linken Menüleiste angezeigt.
- **Individuelle Namen:** Anzeigenamen werden zentral in einer Konfigurationsdatei festgelegt.
- **Eigene Tabs:** Jedes Skript erhält einen eigenen Tab. Der Tab-Name entspricht dem konfigurierten Skriptnamen.
- **Live-Logs:** Die Konsolenausgaben der Skripte werden direkt in der Oberfläche angezeigt.
- **Keine zusätzlichen CMD-Fenster:** Skripte sollen im Hintergrund gestartet werden.
- **Statusanzeige:** Der aktuelle Zustand eines Skripts wird im Menü angezeigt.
- **Automatische Bereinigung:** Nach Beendigung eines Skripts wird dessen Tab geschlossen und das zugehörige Log verworfen.
- **Flexible Konfiguration:** Jeder Benutzer kann eigene Skripte und Pfade hinterlegen, ohne den Python-Code ändern zu müssen.

### Vorgesehene Statusanzeigen

| Status | Bedeutung |
|---|---|
| AUS | Das Skript läuft nicht. |
| RUNNING | Das Skript wird ausgeführt. |
| WAITING | Das Skript wartet auf eine Eingabe, beispielsweise durch `pause`. |

## 🛠️ Technologie

| Komponente | Technologie |
|---|---|
| Programmiersprache | Python 3.11+ |
| Terminal-Oberfläche | [Textual](https://textual.textualize.io/) |
| Darstellung und Formatierung | [Rich](https://github.com/Textualize/rich) |
| Konfiguration | TOML |
| Auszuführende Skripte | Windows CMD / BAT |

Python übernimmt die Steuerung und Darstellung. Die vorhandenen CMD- und BAT-Dateien sollen möglichst unverändert weiterverwendet werden können.

## 📁 Projektstruktur

Die Projektstruktur wird während der Entwicklung schrittweise aufgebaut.

Die angestrebte Struktur:

```text
power_script_for_work/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── config/
│   ├── config.example.toml
│   └── config.toml
│
├── core/
│   └── ...
│
├── ui/
│   └── ...
│
└── styles/
    └── style.tcss
```

Die tatsächliche Struktur kann sich während der Entwicklung noch ändern.

## ⚙️ Entwicklung einrichten

### Voraussetzungen

- Windows
- Python 3.11 oder neuer
- Git
- Visual Studio Code (empfohlen)

Python-Version prüfen:

```cmd
python --version
```

Git-Version prüfen:

```cmd
git --version
```

### Repository herunterladen

```cmd
git clone https://github.com/grayback90/power_script_for_work.git
cd power_script_for_work
```

### Virtuelle Umgebung erstellen

```cmd
python -m venv .venv
```

### Virtuelle Umgebung aktivieren

In der Windows-Eingabeaufforderung (CMD):

```cmd
.venv\Scripts\activate.bat
```

In PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Abhängigkeiten installieren

```cmd
pip install -r requirements.txt
```

### Anwendung starten

```cmd
python main.py
```

## 📝 Konfiguration

Die auszuführenden Skripte sollen zentral über eine TOML-Datei konfiguriert werden.

Jeder Eintrag enthält mindestens einen Anzeigenamen und den Pfad zur auszuführenden CMD- oder BAT-Datei.

Beispiel für das angestrebte Konfigurationsformat:

```toml
[[scripts]]
name = "FTU starten"
path = "C:/Scripts/start_ftu.cmd"

[[scripts]]
name = "FTU stoppen"
path = "C:/Scripts/stop_ftu.cmd"

[[scripts]]
name = "Datenbank zurücksetzen"
path = "C:/Scripts/reset_database.cmd"
```

Die Anzahl der Einträge ist nicht fest vorgegeben. Das Menü soll automatisch anhand der Konfiguration aufgebaut werden.

Die persönliche `config.toml` soll nicht versioniert werden. Stattdessen wird eine Beispielkonfiguration (`config.example.toml`) im Repository bereitgestellt.

*Hinweis: Das hier gezeigte Konfigurationsformat beschreibt den geplanten Zielzustand. Die vollständige Unterstützung wird im Laufe der Entwicklung umgesetzt.*

## 🔄 Entwicklungsablauf

Power Script wird schrittweise gemeinsam entwickelt.

Dabei gelten folgende Grundsätze:

1. Änderungen werden zunächst lokal umgesetzt und getestet.
2. Neue Funktionen werden einzeln entwickelt und nachvollziehbar erklärt.
3. Der Code soll verständlich und möglichst einfach wartbar bleiben.
4. Bestehende CMD- und BAT-Skripte sollen möglichst nicht verändert werden müssen.
5. Commits und Pushes werden ausschließlich vom Repository-Besitzer selbst durchgeführt.

Entwickelt wird direkt auf dem Branch `main`.

## 🚧 Entwicklungsstand

**Aktueller Stand: Frühe Entwicklungsphase**

Die grundlegende Terminal-Oberfläche mit Textual ist bereits vorhanden.

Folgende Bereiche werden schrittweise umgesetzt:

- [ ] Konfigurationsdatei überarbeiten und validieren
- [ ] Dynamisches Menü aus der Konfiguration erstellen
- [ ] Eigene Tabs für jedes Skript implementieren
- [ ] CMD- und BAT-Dateien im Hintergrund starten
- [ ] Live-Ausgabe von `stdout` und `stderr` integrieren
- [ ] Prozessstatus erkennen und anzeigen
- [ ] Umgang mit `pause` und wartenden Prozessen umsetzen
- [ ] Tabs und Logs nach Prozessende automatisch entfernen
- [ ] Fehlerbehandlung ergänzen
- [ ] Start über eine CMD-Datei ermöglichen
- [ ] Portable Bereitstellung für Kollegen vorbereiten

## 📦 Geplante Bereitstellung

Langfristig soll Power Script auch von Kollegen verwendet werden können, ohne dass diese Python selbst installieren oder eine virtuelle Umgebung einrichten müssen.

Dafür wird eine portable Bereitstellung geprüft, die Python und die benötigten Abhängigkeiten mitbringt.

Eine EXE-Datei ist derzeit nicht vorgesehen.

Die konkrete Verteilung und die Kompatibilität mit den IT-Vorgaben werden zu einem späteren Zeitpunkt geklärt.

## 📄 Lizenz

Dieses Projekt steht unter der **GNU General Public License v3.0**.

Weitere Informationen befinden sich in der Datei `LICENSE`.