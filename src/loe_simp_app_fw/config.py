import yaml
import json
import os
import sys
from .logger import Logger

from argparse import ArgumentParser

"""
Workflow of the Config:

# Find config location

- Jupyter Notebook
    - Not use CLI parser
- Normal
    - Use CLI parser

# Load config

- No config
    - Duplicate one from the example
- Have config
    - Nothing

Load config

# Add additional things into config

"""

# Base paths
current_working_dir = os.getcwd()

# -------------------------------
# Parse CLI or not
def isNotebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter

if __name__ == "__main__":
    Logger.error("Running config.py as main! Why?")

# CLI Parser (Only runs once)
config_dir = ""
if not isNotebook():
    # Add CLI
    arguments = ArgumentParser()

    parser = ArgumentParser()
    parser.add_argument("--config", type=str, default="", help="config file overwrites commandline arguments. if not present, a new one will be created")
    
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    config_dir = args.config

# Result of the Parse CLI or not
if config_dir and config_dir.startswith("/"):
    # Start from root
    file_path = config_dir
else:
    # Start from current working dir
    file_path = f"{current_working_dir}/{config_dir}" if config_dir else f"{current_working_dir}/config.yaml"
    
# -------------------------------

class Config:
    # Following parameters should be set at the top-level environment of the project
    _project_root_path = ""
    _example_config_path = "" # The path of _example_config_path relative to _project_root_path
    
    # Following variable will be loaded dynamically
    config = {}

    def __init__(self, config_path: str = file_path):
        Config.config["project root path"] = Config._project_root_path
        Config.config = Config.config | self._load_config(config_path) # Combine two dict
        
    def _load_config(self, path: str) -> dict:
        config = None
        # Copy config file is no local one exists
        if os.path.isfile(path):
            Logger.debug("Config already exists, skips copying.")
            # TODO: Add auto updating

            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            Logger.debug("Load local config successfully.")
            Logger.debug(f"Config: {json.dumps(config, indent=2)}")
        else:
            abs_example_config_path = os.path.join(Config._project_root_path, Config._example_config_path)
            Logger.debug(f"Absolute path of example config: {abs_example_config_path}")
            with open(abs_example_config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            print(json.dumps(config, indent=2))
            Logger.debug("Load example config successfully.")
            Logger.debug(f"Config: {json.dumps(config, indent=2)}")

            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(config, f)

            Logger.info("Duplicate config successfully.")

            Logger.info("First time starting script, please modify config.yaml to the requirements.")
            sys.exit() # Exit script

        # Check config
        if not config:
            Logger.error("Config file empty!")
            raise Exception

        # Check if dev mode
        if config["developer mode"]:
            Logger.warning("Start in developer mode! Config file is override by example config file")
            with open(example_file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            Logger.debug(f"Config: {json.dumps(config, indent=2)}")
        
        return config
