from typing import ClassVar

from .middleware import Middleware
from .model import LogLevels, LogEntry, LogLevelsE, Exceptions

class Logger:
    _middleware: ClassVar[Middleware] = Middleware()
    _isInit: ClassVar[bool] = False
    _isPrintAll: ClassVar[bool] = False
    
    @classmethod
    def bootstrap(
        cls, 
        log_folder_path: str,
        *args,
        log_level: LogLevels = LogLevelsE.INFO.name, 
        print_all: bool = False,
        isMultiprocessing: bool = True,
        **kwargs,
        ) -> None:
        """
        Initialization method for Logger

        Args:
            log_folder_path (str): folder to put log files, should be absolute path
            log_level (LogLevels, optional): log level at which it will be logged. Defaults to INFO.
            buffering (int, optional): size of the writing buffer. Defaults to 4096.
        """
        # Handles when backend gets repeatedly created
        if hasattr(cls._middleware, "backend_s") or hasattr(cls._middleware, "backend_m"):
            cls.error("Backend gets created multiple times")
            raise Exceptions.DuplicatedBootstrap

        # Create backend normally
        cls._isPrintAll = print_all
        cls._middleware.setup(
            log_directory=log_folder_path,
            log_level=log_level,
            isMultiprocessing=isMultiprocessing,
        )

        cls._middleware.log(LogEntry(LogLevelsE.INFO.name, "Logger frontend init successfully"))

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
        cls._middleware.log(log_entry)

    @classmethod
    def _debootstrap(cls) -> None:
        """
        This function is mainly for testing
        """
        # Shutdown old middleware
        cls._middleware.shutdown()
        # Create new one
        cls._middleware = Middleware()
        # Reset settings
        cls._isInit = False
        cls._isPrintAll = False

    @classmethod
    def set_log_level(cls, log_level: LogLevels) -> None:
        cls.info(f"Log level is set to {log_level}, but it is not implemented")

