# power_script_for_work

A terminal tool that controls all my work scripts from one place.

## About

Many small scripts are hard to keep track of. This tool puts them behind a single menu in the terminal. You start a script with one key press and follow its output in a log window next to the menu.

## Features

- Central script that launches and controls all other scripts
- Log window that shows script output
- Terminal user interface with a menu and a log panel

More features will follow.

## Tech Stack

- **Language:** [Python](https://www.python.org/) 3.11 or newer
- **Terminal UI:** [Textual](https://textual.textualize.io/)
- **Styling:** [Rich](https://github.com/Textualize/rich) (used by Textual)

## Configuration

The paths to the scripts are stored in a config file, not in the source code. Everyone who uses the tool sets their own paths. Nobody has to change the code when scripts live in a different folder.

## Getting Started

1. Install Python 3.11 or newer.
2. Clone the repository.
3. Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

4. Create your config file with your script paths.
5. Start the tool:

```bash
python main.py
```

## Status

Early development.

## License

GPL-3.0. See the `LICENSE` file.
