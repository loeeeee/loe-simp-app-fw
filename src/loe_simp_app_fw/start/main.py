from ..logger import Logger
from ..helper import create_folder_if_not_exists
from ..config import FrameworkConfig
from .default import GitIgnore, ProjectConfig

import os

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

def main(project_root_path: str, no_code: bool = False) -> None:
    # Create folders
    Logger.info(f"Init project at {project_root_path}")
    mkdir(project_root_path, "src")
    mkdir(project_root_path, "log")
    mkdir(project_root_path, ".cache")
    Logger.info(f"Finish creating folders")

    # Create config
    file_path = os.path.join(project_root_path, "config-framework.yaml")
    FrameworkConfig.developer_mode = False
    FrameworkConfig.project_directory = project_root_path
    FrameworkConfig.source_directory = os.path.join(project_root_path, "src")
    FrameworkConfig.cache_directory = os.path.join(project_root_path, ".cache")
    FrameworkConfig.project_config_path = os.path.join(project_root_path, "config-project.yaml")
    FrameworkConfig.log_directory = os.path.join(project_root_path, "log")
    FrameworkConfig.dump_example(file_path)
    Logger.info(f"Finish creating config file")

    if not no_code:
        # Create editable config
        file_path = os.path.join(project_root_path, "src", "configuration.py")
        template: str = ProjectConfig.configuration
        write_file_if_not_exists(file_path, template)
        Logger.info(f"Finish creating editable config file")

        # Create example main
        file_path = os.path.join(project_root_path, "src", "main.py")
        template: str = ProjectConfig.main
        write_file_if_not_exists(file_path, template)
        Logger.info(f"Finish creating example main file")

        # Create gitignore
        file_path = os.path.join(project_root_path, ".gitignore")
        git_ignore = GitIgnore.python + GitIgnore.this
        write_file_if_not_exists(file_path, git_ignore)
        Logger.info(f"Finish creating gitignore")
    
    return