from ..logger import Logger
from ..helper import create_folder_if_not_exists
from .default import ConfigExample, GitIgnore, Config

import os
import yaml

def mkdir(root_path: str, folder_name: str) -> None:
    Logger.debug(f"Create {folder_name} folder")
    path = os.path.join(root_path, folder_name)
    create_folder_if_not_exists(path)
    return

def write_file_if_not_exists(file_path: str, content: str) -> None:
    if not os.path.isfile(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        Logger.info("Successfully write the file")
    else:
        Logger.warning(f"File already exists at {file_path}, skipping file creation")
    return

def main(project_root_path: str) -> None:
    # Create folders
    Logger.info(f"Init project at {project_root_path}")
    mkdir(project_root_path, "src")
    mkdir(project_root_path, "log")
    mkdir(project_root_path, ".cache")
    Logger.info(f"Finish creating folders")

    # Create example config
    file_path = os.path.join(project_root_path, "config-example.yaml")
    example_config: Config = ConfigExample.this
    example_config["cache directory"] = os.path.join(project_root_path, ".cache")
    example_config["project directory"] = project_root_path
    write_file_if_not_exists(file_path, yaml.safe_dump(example_config, None, indent=2))
    Logger.info(f"Finish creating config example")

    # Create gitignore
    file_path = os.path.join(project_root_path, ".gitignore")
    git_ignore = GitIgnore.python + GitIgnore.this
    write_file_if_not_exists(file_path, git_ignore)
    Logger.info(f"Finish creating gitignore")
    
    return