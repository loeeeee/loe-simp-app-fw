from enum import Enum
from io import TextIOWrapper
import os
import datetime
from typing import ClassVar, Literal, List, TypeAlias, Union
from dataclasses import dataclass, field
import multiprocessing
from multiprocessing import JoinableQueue, Process, Event
from multiprocessing.synchronize import Event as EventType
from queue import Empty
import time

# Do not write the Log until the explicit initialization of the logger
LogLevels: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class LogLevelsE(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


@dataclass
class LogEntry:
    level: LogLevels
    message: str

    # Internal
    consumed: bool = field(default=False, kw_only=True)

    def __str__(self) -> str:
        return f"{datetime.datetime.now()} {self.level.upper()}: {self.message}\n"


class _Logger(Process):
    def __init__(
        self, 
        log_queue: JoinableQueue, 
        log_directory: Union[str, os.PathLike], 
        log_buffering: int,
        log_level: LogLevels, 
        isFinish: EventType,
        *args, 
        ) -> None:
        super().__init__(
            name="Logger Backend"
            )
        self._level: int = getattr(LogLevelsE, log_level).value
        self._buffer: int = log_buffering
        self._log_directory = log_directory
        self._date: datetime.date = datetime.date.today()
        self._isFinish = isFinish
        self._history_length: int = 3000
        self._last_write_time: float = time.time()
        self._write_interval: float = 2.0

        self.queue: JoinableQueue = log_queue
        self.file_handler = self.create_file_handler()
        self.debug_file_handler = open(
            os.path.join(log_directory, "debug.log"),
            "w",
            encoding = "utf-8",
            buffering = log_buffering,
        )
        self.log_history: List[LogEntry] = []

    def run(self) -> None:
        # Main loop
        while not self._isFinish.is_set() or not self.queue.empty():
            try:
                log = self.queue.get(timeout=self._write_interval)
            except (multiprocessing.TimeoutError, Empty):
                self.log_history.append(
                    LogEntry(
                        LogLevelsE.DEBUG.name,
                        "A timeout happened because no logs are received"
                    )
                )
            else:
                # Save all to temporary log
                self.log_history.append(log)
                self.queue.task_done()
            finally:
                # Always write with intervals
                now = time.time()
                if now - self._last_write_time > self._write_interval:
                    self.write()
                    self._last_write_time = now
                    self.update_file_handler()

        # Finish up
        self.log_history.append(
            LogEntry(
                LogLevelsE.INFO.name,
                "Finish signal received, saving log file and exiting"
            )
        )
        self.write()
        self.debug_file_handler.writelines(
            [str(log) for log in self.log_history]
        )
        self.debug_file_handler.close()
        self.file_handler.close()
        self.close()

    def write(self) -> None:
        # Write important ones
        to_write: List[str] = []
        for history_log in self.log_history:
            if not history_log.consumed and getattr(LogLevelsE, history_log.level).value >= self._level:
                history_log.consumed = True
                to_write.append(str(history_log))
        
        self.file_handler.writelines(to_write)

        # Trimming
        if len(self.log_history) > self._history_length * 2:
            self.log_history.append(
                LogEntry(
                    LogLevelsE.DEBUG.name,
                    "Log history length exceeded, trimming"
                )
            )
            self.log_history = self.log_history[-self._history_length:]

    def update_file_handler(self) -> None:
        # For persistent operations
        today = datetime.date.today()
        if today != self._date:
            self.file_handler = self.create_file_handler()
            self.queue.put(LogEntry(LogLevelsE.INFO.name, f"Update log file handler successful"))
            self._date = today
    
    def create_file_handler(self) -> TextIOWrapper:
        log_file_location: str = os.path.join(self._log_directory, f"{datetime.date.today()}.log")
        if not os.path.isfile(log_file_location) and not os.path.isdir(log_file_location):
            with open(log_file_location, "w", encoding="utf-8"):
                print("Log file created successfully.")
        return open(
            log_file_location,
            "a", 
            encoding="utf-8", 
            buffering=self._buffer
            )
            

class Logger:
    _backend: ClassVar[_Logger]
    _queue: ClassVar[JoinableQueue] = JoinableQueue()
    _isInit: ClassVar[bool]
    _isFinish: ClassVar[EventType] = Event()

    @classmethod
    def bootstrap(
        cls, 
        log_folder_path: str,
        *args,
        log_level: LogLevels = LogLevelsE.INFO.name, 
        buffering: int = 4096,
        **kwargs,
        ) -> None:
        """
        Initialization method for Logger

        Args:
            log_folder_path (str): folder to put log files, should be absolute path
            log_level (LogLevels, optional): log level at which it will be logged. Defaults to INFO.
            buffering (int, optional): size of the writing buffer. Defaults to 4096.
        """
        cls._backend = _Logger(
            log_queue = cls._queue, 
            log_directory = log_folder_path,
            log_level = log_level,
            log_buffering = buffering,
            isFinish = cls._isFinish
            )
        cls._backend.start()
        cls._isInit = True
        cls._print(LogEntry(LogLevelsE.INFO.name, "Logger init successfully"))

    @classmethod
    def debug(cls, msg: str) -> None:
        cls._logging(LogEntry(LogLevelsE.DEBUG.name, msg))
    
    @classmethod
    def info(cls, msg: str) -> None:
        cls._logging(LogEntry(LogLevelsE.INFO.name, msg))

    @classmethod
    def warning(cls, msg: str) -> None:
        cls._logging(LogEntry(LogLevelsE.WARNING.name, msg))

    @classmethod
    def error(cls, msg :str) -> None:
        cls._logging(LogEntry(LogLevelsE.ERROR.name, msg))
    
    @classmethod
    def _logging(cls, log_entry: LogEntry) -> None:
        cls._queue.put(log_entry)
        if not cls._isInit:
            print(log_entry, end="")

    @classmethod
    def _finish(cls) -> None:
        cls._isFinish.set()
        cls._print(LogEntry(LogLevelsE.DEBUG.name, f"Logger frontend flags: {cls._isFinish.is_set()}"))
        cls._queue.join()

    @classmethod
    def set_log_level(cls, log_level: LogLevels) -> None:
        cls.info(f"Log level is set to {log_level}, but it is not implemented")

    @staticmethod
    def _print(log: LogEntry) -> None:
        print(log, end="")


def main():
    Logger.bootstrap(
        "./log"
    )
    Logger.debug("COOL MESSAGE")
    Logger.error("Not cool")
    Logger.error("Not cool")
    Logger.error("Not cool")
    Logger.error("Not cool")
    Logger.error("Not cool")
    Logger.error("Not cool")
    Logger._finish()

if __name__ == "__main__":
    main()