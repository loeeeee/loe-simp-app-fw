import os
import datetime
from typing import Literal, Dict, Tuple, List, TypeAlias
import tempfile
from io import TextIOWrapper
from .helper import create_folder_if_not_exists, ProjectRootChanged
import atexit

# Do not write the Log until the explicit initialization of the logger
LogLevels: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR"]

class DebugQueue:
    def __init__(self, number_of_message_to_keep: int = 5000) -> None:
        self._queue: List[str] = []
        self._last: int = number_of_message_to_keep
        self.log_location: str = ""

    def append(self, message: str) -> None:
        self._queue.append(message)
        # Trim excessive
        if len(self._queue) >= 1.5 * self._last:
            self._queue = self._queue[-self._last:]
        return

    def __len__(self) -> int:
        return len(self._queue)

    def dump(self) -> None:
        file_path: str = os.path.join(self.log_location, "debug.log")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("".join(self._queue[-self._last:]))

class Logger:
    # Following parameters should be set at the top-level environment of the project
    _log_folder_path = "" # The abs _log_folder_path
    
    # Internal variable
    _log_buffer: List[Tuple[LogLevels, str]] = []
    _isInit: bool = False
    _log_file_handle: TextIOWrapper = tempfile.TemporaryFile("w")
    _log_level: LogLevels = "INFO"
    _debug_queue: DebugQueue = DebugQueue()
    
    # Constant
    numerical_map: Dict[LogLevels, Literal[0, 1, 2, 3]]= {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3
    }

    @classmethod
    def _log_location(cls):
        file_name = f"{datetime.date.today()}.log"
        return os.path.join(cls._log_folder_path, file_name)

    @classmethod
    def _create_log_file(cls):
        if not os.path.isfile(cls._log_location()) and not os.path.isdir(cls._log_location()):
            with open(cls._log_location(), "w", encoding="utf-8"):
                print("Create log file successfully.")

    def __init__(self, log_folder_path: str, project_root_path: str = os.getcwd(), log_level: LogLevels = "INFO", buffering: int = 1024):
        """Init Logger

        Args:
            log_folder_path (str): path to log folder relative to project root path
            project_root_path (str, optional): DEPRECATED! DOES NOTHING

        Raises:
            ProjectRootChanged: Project root directory should not be changed once set
        """
        # Save input
        type(self)._log_folder_path = os.path.abspath(log_folder_path)
        type(self)._log_level = log_level

        self._debug_queue.log_location = self._log_folder_path

        # Sanity check
        if self._log_folder_path and log_folder_path and not os.path.samefile(log_folder_path, self._log_folder_path):
            self.error("One should not change project root path")
            raise ProjectRootChanged

        # Create log folder
        if not os.path.isfile(self._log_folder_path) and not os.path.isdir(self._log_folder_path):
            create_folder_if_not_exists(self._log_folder_path)

        # Create file IO handle
        self._log_file_handle.close()
        type(self)._log_file_handle = open(self._log_location(), "a", encoding="utf-8", buffering=buffering)

        # Save previous logs
        self._log_file_handle.writelines(f"\n{datetime.datetime.now()} INIT Logger successful\n")
        for entry in self._log_buffer:
            composed_log_entry = self._log_composer(*entry)
            print(composed_log_entry)
            self._log_file_handle.writelines(composed_log_entry)
        
        # Empty log buffer
        type(self)._log_buffer = []

        # Update flags
        type(self)._isInit = True
        print(f"Logger init process finished, Logger isInit is set to {self._isInit}.")
        print(f"Now respecting log level, {log_level}.")

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
    def set_log_level(cls, level: LogLevels) -> None:
        cls._log_level = level
        Logger.warning(f"Log level is manually set to {level}")

    @classmethod
    def _log(cls, level: LogLevels, msg: str) -> None:
        # Compose log
        composed_log_entry = cls._log_composer(level, msg)
        if cls._isInit:
            # Log level filter
            if cls.numerical_map[level] >= cls.numerical_map[cls._log_level]:
                # The file handler is only to make static checker happy
                # Write to file
                cls._log_file_handle.writelines(composed_log_entry)
            
            # Keep track of the latest entry
            cls._debug_queue.append(composed_log_entry)
        else:
            # Write to buffer, not file
            cls._log_buffer.append((level, msg))
            print(composed_log_entry)
        return

    @staticmethod
    def _log_composer(level: LogLevels, msg: str) -> str:
        return f"{datetime.datetime.now()} {level.upper()}: {msg}\n"
        

@atexit.register
def clean_log_buffer():
    # Clean up logger buffer when crashing
    Logger._log_file_handle.close()
    Logger._debug_queue.dump()

def logger_showoff() -> None:
    # Demonstrate the logger
    Logger("log")
    print(f"Today is {datetime.date.today()}")
    Logger.info("LOGGER IS DeMoInG.")

if __name__ == "__main__":
    logger_showoff()