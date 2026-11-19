
@echo off

REM Wechselt in das Verzeichnis, in dem diese BAT-Datei liegt.
cd /d "%~dp0"

REM Prüft, ob der Python-Interpreter der virtuellen Umgebung existiert.
if not exist ".venv\Scripts\python.exe" (
    echo FEHLER: Python-Umgebung wurde nicht gefunden.
    echo Bitte pruefe, ob der Ordner .venv vorhanden ist.
    pause
    exit /b 1
)

REM Startet die Power-Script-Anwendung mit der virtuellen Umgebung.
".venv\Scripts\python.exe" "main.py"

REM Hält das Fenster bei einem Fehler offen, damit die Meldung lesbar bleibt.
if errorlevel 1 (
    echo.
    echo Die Anwendung wurde mit einem Fehler beendet.
    pause
)
