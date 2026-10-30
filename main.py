from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static


class PowerScriptApp(App):
    TITLE = "Power Script"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Hello, Textual!")
        yield Footer()


if __name__ == "__main__":
    PowerScriptApp().run()