#modul that can read toml-files
import tomllib
#build data-paths
from pathlib import Path
#path to the config-file
CONFIG_PATH = Path(__file__).parent / "config.toml"

#function to load the config file
def load_config():
    #check if the file is there then load it and return the data else show a error message
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("No config found.")
    with open(CONFIG_PATH, "rb") as f:
        data = tomllib.load(f)

    return data

