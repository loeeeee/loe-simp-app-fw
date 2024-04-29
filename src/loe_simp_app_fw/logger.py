import os
import datetime
from io import TextIOWrapper
from typing import Optional, IO
from .helper import create_folder_if_not_exists, ProjectRootChanged

# Do not write the Log until the explicit initialization of the logger

class Logger:
    # Following parameters should be set at the top-level environment of the project
    _project_root_path = ""
    _log_folder_path = "" # The path of _example_config_path relative to _project_root_path
    
    # Internal variable
    _log_buffer = []
    _isInit = False
    _log_file_handle: Optional[IO] = None
    
    @classmethod
    def _log_location(cls):
        file_name = f"{datetime.date.today()}.log"
        return os.path.join(cls._project_root_path, cls._log_folder_path, file_name)

    @classmethod
    def _create_log_file(cls):
        if not os.path.isfile(cls._log_location()) and not os.path.isdir(cls._log_location()):
            with open(cls._log_location(), "w", encoding="utf-8") as f:
                print("Create log file successfully.")

    def __init__(self, log_folder_path: str, project_root_path: str = os.getcwd()):
        """Init Logger

        Args:
            log_folder_path (str): path to log folder relative to project root path
            project_root_path (str, optional): path to project top-level directory. Defaults to os.getcwd().
                                                The parent folder of that would be os.path.dirname(os.path.realpath(__file__)).

        Raises:
            ProjectRootChanged: Project root directory should not be changed once set
        """
        # Sanity check
        if self._project_root_path and project_root_path and not os.path.samefile(project_root_path, self._project_root_path):
            self.error("One should not change project root path twice")
            raise ProjectRootChanged

        # Save input
        self._log_folder_path = log_folder_path
        self._project_root_path = project_root_path

        # Create log folder
        folder_name = os.path.join(self._project_root_path, self._log_folder_path)
        if not os.path.isfile(folder_name) and not os.path.isdir(folder_name):
            create_folder_if_not_exists(folder_name)

        # Create file IO handle
        self._log_file_handle = open(self._log_location(), "a", encoding="utf-8")

        # Save previous logs
        self._log_file_handle.writelines(f"\n{datetime.datetime.now()} INIT Logger successful\n")
        self._log_file_handle.writelines("".join(self._log_buffer))
        
        # Empty log buffer
        self._log_buffer = []

        # Update flags
        self._isInit = True
        print(f"Logger init process finished, Logger isInit is set to {self._isInit}")

    @classmethod
    def info(cls, msg: str) -> None:
        cls._log("INFO", msg)

    @classmethod
    def debug(cls, msg: str) -> None:
        cls._log("DEBUG", msg)

    @classmethod
    def warning(cls, msg: str) -> None:
        cls._log("WARNING", msg)

    @classmethod
    def error(cls, msg :str) -> None:
        cls._log("ERROR", msg)

    @classmethod
    def _log(cls, level: str, msg: str) -> None:
        # Compose log
        composed_log_entry = f"{datetime.datetime.now()} {level.upper()}: {msg}\n"
        if cls._isInit and isinstance(cls._log_file_handle, TextIOWrapper): 
            # The file handler is only to make static checker happy
            # Write to file
            try:
                cls._log_file_handle.writelines(composed_log_entry)
            except FileNotFoundError:
                cls._create_log_file()
        else:
            # Write to buffer, not file
            cls._log_buffer.append(composed_log_entry)
            print(composed_log_entry)
        return
        

def logger_showoff() -> None:
    # Demonstrate the logger
    Logger("log")
    print(f"Today is {datetime.date.today()}")
    Logger.info("LOGGER IS DeMoInG.")

if __name__ == "__main__":
    logger_showoff()