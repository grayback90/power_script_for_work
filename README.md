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

## Setup on a New Machine

Follow these steps on any computer where you want to run or develop the tool.

### 1. Install the requirements

- **Python 3.11 or newer.** Check your version:

  ```bash
  python --version
  ```

  On Windows, `py --version` also works. If Python is missing, install it from [python.org](https://www.python.org/downloads/). On Windows, tick "Add Python to PATH" during the installation.

- **Git.** Check it with:

  ```bash
  git --version
  ```

### 2. Clone the repository

```bash
git clone https://github.com/grayback90/power_script_for_work.git
cd power_script_for_work
```

If the repository is private, Git asks you to log in to GitHub. Use your GitHub account or a personal access token. Alternatively, set up an SSH key and clone with the SSH URL.

### 3. Create a virtual environment

```bash
python -m venv .venv
```

The folder `.venv` holds a Python installation that belongs only to this project. It is not part of the repository.

### 4. Activate the virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows CMD:

```
.venv\Scripts\activate.bat
```

Linux and macOS:

```bash
source .venv/bin/activate
```

You see `(.venv)` in front of your prompt when it works. If PowerShell blocks the script, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 5. Install the dependencies

```bash
pip install -r requirements.txt
```

### 6. Create your config file

The paths to your scripts are stored in a local config file. It is not part of the repository, so every machine needs its own copy. Create `config.toml` in the project folder and enter the paths to your scripts. Details follow in the Configuration section.

### 7. Start the tool

```bash
python main.py
```

Press `q` to quit.

## Daily Workflow

Activate the virtual environment first (step 4). Then:

```bash
git pull                      # get the latest changes
python main.py                # run the tool
git status                    # see what you changed
git add .
git commit -m "Describe your change"
git push                      # upload your changes
```

Always run `git pull` before you start working. Always run `git push` when you finish. This keeps all machines in sync.

### Adding a new dependency

```bash
pip install <package>
pip freeze > requirements.txt
```

Commit the changed `requirements.txt`. On the other machine, run `pip install -r requirements.txt` after `git pull`.

## Configuration

The paths to the scripts are stored in a config file, not in the source code. Everyone who uses the tool sets their own paths. Nobody has to change the code when scripts live in a different folder.

The file `config.toml` is listed in `.gitignore`. Your personal paths never end up in the repository.

## Troubleshooting

- **`python` is not found:** Try `py` (Windows) or `python3` (Linux and macOS).
- **`pip install` fails outside the virtual environment:** Activate `.venv` first (step 4).
- **Window looks broken or shows no colors:** Use a modern terminal such as Windows Terminal.

## Status

Early development.

## License

GPL-3.0. See the `LICENSE` file.