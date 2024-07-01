from typing import Annotated, ClassVar, List, Dict, Any
import yaml
import os
from .logger import Logger, LogLevels

class NotInitialized(Exception):
    pass


class BaseConfig:
    @classmethod
    def _all_variables(cls) -> Dict[str, Any]:
        all_variables = {k: v for k, v in vars(cls).items()}
        del all_variables["__module__"]
        del all_variables["__annotations__"]
        del all_variables["__doc__"]
        return all_variables

    @classmethod
    def dump_example(cls, file_path: str) -> None:
        if not os.path.isfile(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml.safe_dump(cls._all_variables()))
            Logger.info("Successfully write the file")
        else:
            Logger.warning(f"File already exists at {file_path}, skipping file creation")
        return

    @classmethod
    def load(cls, file_path: str, update: bool = True) -> None:
        # No file found case
        if not os.path.isfile(file_path):
            Logger.error(f"Cannot find file at {file_path}")
            raise NotInitialized

        # Find existing files
        with open(file_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
        Logger.info("Successfully load the file")

        # Find updates
        existing_keys_in_code: List[str] = list(cls._all_variables().keys())
        if content:
            for key, value in content.items():
                try:
                    ind = existing_keys_in_code.index(key)
                except ValueError:
                    Logger.warning(f"{key} are deleted in the code, removing it from config")
                else:
                    # Note what code has and config does not
                    existing_keys_in_code.pop(ind)
                    # Load the config by the way
                    setattr(cls, key, value)
        
        # Write example back
        if existing_keys_in_code and update:
            Logger.info(f"Find config update in code, {existing_keys_in_code}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml.safe_dump(cls._all_variables()))
            Logger.info("Successfully update the file")
        else:
            Logger.info("No update found in code")
        return


class FrameworkConfig(BaseConfig):
    developer_mode: ClassVar[Annotated[bool, "Ignoring yaml config file"]]      = False
    # Anchors
    project_directory: ClassVar[Annotated[str, "Root folder of the project"]]   = ""
    project_config_path: ClassVar[Annotated[str, "Path to config yaml file"]]   = ""
    source_directory: ClassVar[Annotated[str, "Path to code directory"]]        = ""
    # Cache system
    cache_directory: ClassVar[Annotated[str, "Folder for storing cache"]]       = ""
    cache_time_to_live: ClassVar[Annotated[int, "Auto expire cache"]]           = 7
    # Log system
    log_directory: ClassVar[Annotated[str, "Folder for storing log files"]]     = ""
    log_level: ClassVar[Annotated[LogLevels, "Log levels"]]                     = "INFO"
    log_buffer_size: ClassVar[Annotated[int, "Size of buffer"]]                 = 2048

