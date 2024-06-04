import yaml
import json
import os
import sys
from .logger import Logger
from .helper import ProjectRootChanged

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

# Setup flags
isCLI = False

# Parse CLI or not
def isNotebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__ # het_python() is globally available when using jupyter notebook
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
    parser.add_argument("--config", type=str, default="", help="config file overwrites command line arguments. if not present, a new one will be created")
    
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    config_dir = args.config
else:
    Logger.info("Jupyter Notebook environment detected")


# Result of the Parse CLI or not
if config_dir.startswith("/"):
    # Start from root
    Logger.info(f"Loading config from {config_dir}")
    isCLI = True
elif not config_dir.startswith("/") and config_dir:
    # Start from current working dir
    config_dir = f"{current_working_dir}/{config_dir}"
    Logger.info(f"Loading config from {config_dir}")
    isCLI = True
else:
    Logger.debug("No config information can be inferred from the CLI")
    
# -------------------------------

class Config:
    # Following parameters should be set at the top-level environment of the project
    _project_root_path = ""
    _example_config_path = "" # The path of _example_config_path relative to _project_root_path
    
    # Following variable will be loaded dynamically
    config = {}

    def __init__(
        self, 
        config_path: str, 
        project_root_path: str = current_working_dir, 
        example_config_path: str = "config-example.yaml", 
        respect_CLI: bool = False
        ) -> None:
        """Load config file from given path

        Args:
            config_path (str): path to config, should be a yaml file
            project_root_path (str, optional): path to project top level. Defaults to current working directory.
            example_config_path (str, optional): path to config example. Defaults to "".
            respect_CLI (CLI, optional): whether CLI will overwrite the config choice of config_path. Defaults to False.
        """
        # Sanity check
        ## No on-the-fly update of project root path
        if Config._project_root_path and project_root_path and not os.path.samefile(project_root_path, Config._project_root_path):
            Logger.error("One should not change project root path twice.")
            Logger.error(f"Original project root path: {Config._project_root_path}")
            Logger.error(f"Updated project root path: {project_root_path}")
            raise ProjectRootChanged

        # Convert relative path to absolute path
        config_path = os.path.join(project_root_path, config_path)
        Logger.debug(f"Absolute config path is {config_path}")
        example_config_path = os.path.join(project_root_path, example_config_path)
        Logger.debug(f"Absolute config path is {config_path}")

        ## Check example config file
        if not example_config_path or not os.path.isfile(example_config_path):
            Logger.warning("Example config path not valid")

        ## Check config path
        if not os.path.isfile(config_path):
            Logger.error(f"{config_path} is not valid file.")

        # Do the loading conditionally
        if respect_CLI and isCLI:
            Logger.info("Config is already inited by CLI.")
        else:
            Logger.info("Config is not init by CLI.")
            Config._project_root_path = project_root_path
            Config._example_config_path = example_config_path
            Config.config["project root path"] = Config._project_root_path
            Config.config = Config.config | self._load_config(config_path) # Combine two dict
        
    def _load_config(self, path: str) -> dict:
        config = None
        abs_example_config_path = os.path.join(Config._project_root_path, Config._example_config_path)
        Logger.debug(f"Example config path is {abs_example_config_path}")
        # Copy config file is no local one exists
        if os.path.isfile(path):
            Logger.debug("Config already exists, skips copying.")
            # TODO: Add auto updating

            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            Logger.debug("Load local config successfully.")
            Logger.debug(f"Config: {json.dumps(config, indent=2)}")
        else:
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
            with open(abs_example_config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            Logger.debug(f"Config: {json.dumps(config, indent=2)}")
        
        return config

# -------------------------------
Logger.debug(f"isCLI is set to {isCLI}")

# Init Config if CLI arguments are parsed successfully
if __name__ != "__main__" and isCLI:
    Logger.info(f"Receive CLI arguments")
    Config(config_dir)
