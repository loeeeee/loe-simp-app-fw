from io import TextIOWrapper
from typing import TypeAlias, Literal, List, Union
from enum import Enum, auto
from dataclasses import dataclass, field
import datetime
import os
import time

LogLevels: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class LogLevelsE(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


ResourceLocator: TypeAlias = Union[str, os.PathLike]
Backend: TypeAlias = Literal["NONE", "SEPARATE", "MAIN"]

class BackendE(Enum):
    NONE = auto()
    SEPARATE = auto()
    MAIN = auto()


class Exceptions:
    class DuplicatedBootstrap(Exception):
        pass

    class BackendProcessNotDead(Exception):
        pass

    class QueueCorruption(Exception):
        pass

    class NoBackendFound(Exception):
        pass

    class InvalidBackendSwitch(Exception):
        pass

    class UnexpectedBackend(Exception):
        pass


@dataclass
class LogEntry:
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now, kw_only=True)
    level: LogLevels
    message: str

    # Internal
    consumed: bool = field(default=False, kw_only=True)

    def __str__(self) -> str:
        return f"{str(self.timestamp.time())} {self.level.upper()}: {self.message}\n"


class BackendHelper:
    def __init__(
        self,
        log_directory: ResourceLocator,
        log_level: LogLevels,
        *args,
        write_interval: float = 5.0,
        debug_log_length: int = 5000,
        noFileHandler: bool = False,
        **kwargs,
        ) -> None:
        # Settings
        self._directory: ResourceLocator = log_directory
        self._level: LogLevels = getattr(LogLevelsE, log_level).value
        self._date: datetime.date = datetime.date.today()
        self._write_interval: float = write_interval
        self._debug_log_length: int = debug_log_length

        # Internal variables
        self.logs: List[LogEntry] = []
        self.last_write_time: float = time.time()
        if not noFileHandler:
            self.normal_file_handler: TextIOWrapper = self._create_normal_file_handler()

    def _write_normal_log(self, noInterval: bool = False) -> None:
        # Judge if the interval is reached
        now = time.time()
        if now - self._write_interval >= self.last_write_time or noInterval:
            to_write: List[str] = self._get_unconsumed_normal_log()
            # Write normal logs to file, this can be either one-shot or not
            self.normal_file_handler.writelines(to_write)
            self.last_write_time = now
            self.logs.append(
                LogEntry(LogLevelsE.DEBUG.name, "One timed write happens")
            )
        return

    def _write_debug_log(self) -> None:
        # Write debug files, this is a one-shot operation
        with self._create_debug_file_handler() as handler:
            handler.writelines(
                [str(log) for log in self.logs[-self._debug_log_length:]]
            )

    def _get_unconsumed_normal_log(self) -> List[str]:
        # Write important ones normally
        to_write: List[str] = []
        for history_log in self.logs:
            if not history_log.consumed and getattr(LogLevelsE, history_log.level).value >= self._level:
                history_log.consumed = True
                to_write.append(str(history_log))

        # Now it is safe to trim log history
        self.logs = self.logs[-self._debug_log_length:]
        return to_write
            
    def _update_normal_file_handler(self) -> None:
        # For persistent operations
        today = datetime.date.today()
        if today != self._date:
            self.normal_file_handler = self._create_normal_file_handler()
            self.logs.append(LogEntry(LogLevelsE.INFO.name, "Update log file handler successful"))
            self._date = today
    
    def _create_normal_file_handler(self) -> TextIOWrapper:
        log_file_location: str = os.path.join(self._directory, f"{datetime.date.today()}.log")
        if not os.path.isfile(log_file_location) and not os.path.isdir(log_file_location):
            with open(log_file_location, "w", encoding="utf-8"):
                self.logs.append(
                    LogEntry(LogLevelsE.INFO.name, "Log file created successfully.")
                )
        return open(
            log_file_location,
            "a", 
            encoding="utf-8",
            buffering=1,
            )

    def _create_debug_file_handler(self) -> TextIOWrapper:
        return open(
            os.path.join(self._directory, f"debug.log"),
            "w", 
            encoding="utf-8", 
            )