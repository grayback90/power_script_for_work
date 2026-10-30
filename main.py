from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, RichLog, Static

from config import load_config


class PowerScriptApp(App):
    TITLE = "Power Script"
    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("1", "run_dummy('Script 1')", "Script 1"),
        ("2", "run_dummy('Script 2')", "Script 2"),
        ("3", "run_dummy('Script 3')", "Script 3"),
        ("c", "clear_log", "Clear log"),
        ("q", "quit", "Quit"),
    ]

    def build_menu_text(self) -> str:
        scripts = load_config()["scripts"]
        lines = []
        for number, entry in enumerate(scripts, start=1):
            lines.append(f"{number}) {entry['name']}")
        script_block = "\n".join(lines)
        return (
            f"[b]Scripts[/b]\n\n{script_block}\n\n"
            "[b]Other[/b]\n\nC) Clear log\nQ) Quit"
        )

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Static(self.build_menu_text(), id="menu")
            yield RichLog(id="log", markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#menu").border_title = "Menu"
        self.query_one("#log").border_title = "Log"
        self.write_log("SYSTEM", "Initialization finished")

    def write_log(self, source: str, message: str) -> None:
        time = datetime.now().strftime("%H:%M:%S")
        line = f"[dim]{time}[/dim] | [cyan]{source:<8}[/cyan] | {message}"
        self.query_one("#log", RichLog).write(line)

    def action_run_dummy(self, name: str) -> None:
        self.write_log("SCRIPT", f"{name} would start now")

    def action_clear_log(self) -> None:
        self.query_one("#log", RichLog).clear()


if __name__ == "__main__":
    PowerScriptApp().run()