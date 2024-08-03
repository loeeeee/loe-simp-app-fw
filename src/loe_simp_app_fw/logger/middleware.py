from multiprocessing import Event, JoinableQueue
from typing import Callable
from multiprocessing.synchronize import Event as EventType

from .backend_m import Backend as BackendM
from .backend_s import Backend as BackendS
from .model import Backend, Exceptions, LogEntry, LogLevelsE, ResourceLocator, LogLevels

_logo: str = """
    __              _          _____ _                      ___    ____  ____     _______       __
   / /   ____  ___ ( )_____   / ___/(_)___ ___  ____       /   |  / __ \\/ __ \\   / ____/ |     / /
  / /   / __ \\/ _ \\|// ___/   \\__ \\/ / __ `__ \\/ __ \\     / /| | / /_/ / /_/ /  / /_   | | /| / / 
 / /___/ /_/ /  __/ (__  )   ___/ / / / / / / / /_/ /    / ___ |/ ____/ ____/  / __/   | |/ |/ /  
/_____/\\____/\\___/ /____/   /____/_/_/ /_/ /_/ .___(_)  /_/  |_/_/   /_/      /_/      |__/|__/   
                                            /_/                                                   
   
"""

class Middleware:
    __slots__ = [
        "log", 
        "_current_backend", 
        "queue", 
        "isFinish", 
        "_isSetUp",
        "_directory",
        "_level",
        "_write_interval",
        "backend_s",
        "backend_m",
        "_debug_log_length",
        "_isMultiprocessing",
        ]

    def __init__(
        self,
        *args,
        **kwargs,
        ) -> None:
        self.log: Callable[[LogEntry], None] = self._log_none

        self.backend_m: BackendM
        self.backend_s: BackendS
        self._current_backend: Backend = "NONE"

        self.queue: JoinableQueue = JoinableQueue()
        self.isFinish: EventType = Event()

        self._directory: ResourceLocator
        self._level: LogLevels
        self._write_interval: float
        self._debug_log_length: int
        self._isSetUp: bool = False
        self._isMultiprocessing: bool = True

        self._print_logo()

    # ---------------------------- INTERNAL LOG METHODS ------------------------------

    def _log_none(self, log: LogEntry) -> None:
        self.queue.put(log)
        return

    def _log_backend_m(self, log: LogEntry) -> None:
        self.backend_m.log(log)
        return

    def _log_backend_s(self, log: LogEntry) -> None:
        self.queue.put(log)
        return

    # ---------------------------- API METHODS ------------------------------

    def setup(
        self,
        log_directory: ResourceLocator, 
        log_level: LogLevels, 
        *args, 
        write_interval: float = 5.0, 
        debug_log_length: int = 5000,
        isMultiprocessing: bool = True, 
        **kwargs
        ) -> None:
        if self._isSetUp:
            self.log(
                LogEntry(
                    LogLevelsE.ERROR.name,
                    "Setup happens twice"
                )
            )
            raise Exceptions.DuplicatedBootstrap

        self._directory = log_directory
        self._level = log_level
        self._write_interval = write_interval
        self._debug_log_length = debug_log_length
        self._isMultiprocessing = isMultiprocessing

        self._judge_backend("NONE")
        if isMultiprocessing:
            self._switch_none_to_backend_s()
        else:
            self._switch_none_to_backend_m()
        self._isSetUp = True

    def shutdown(self) -> None:
        # Sanity check
        if self._isMultiprocessing:
            try:
                self._judge_backend("SEPARATE")
            except Exceptions.UnexpectedBackend:
                self.log(
                    LogEntry(
                        LogLevelsE.WARNING.name,
                        "No backend in separate process found for a multiprocessing logger"
                    )
                )
        else:
            try:
                self._judge_backend("MAIN")
            except Exceptions.UnexpectedBackend:
                self.log(
                    LogEntry(
                        LogLevelsE.WARNING.name,
                        "No backend in main process found"
                    )
                )

        # Early shutdown
        if self._current_backend == "NONE":
            self.log(
                LogEntry(
                    LogLevelsE.WARNING.name,
                    "Logger is never setup properly, backend is NONE"
                )
            )
            # Dumping log into stdout
            while not self.queue.empty():
                self._print(self.queue.get_nowait())
                self.queue.task_done()
            return
        
        # Shutdown sequence
        if self._current_backend == "SEPARATE":
            self._switch_backend_s_to_backend_m()
            if self.backend_s.is_alive():
                self.log(
                    LogEntry(
                        LogLevelsE.ERROR.name,
                        "Backend in separate process is still alive"
                    )
                )
        if self._current_backend == "MAIN":       
            self._switch_backend_m_to_none()
            self.log(
                LogEntry(
                    LogLevelsE.INFO.name,
                    "All file backend shutdown, logs no longer save to file"
                )
            )

    # ---------------------------- START METHODS ------------------------------

    def _switch_none_to_backend_m(
        self,
    ) -> None:
        """
        User do not want to have separate process
        """
        # Bootstrap backend M
        self._bootstrap_backend_m()
        # Move cached log to backend
        self._clean_up_queue()

    def _switch_none_to_backend_s(
        self,
        ) -> None:
        """
        Bootstrap the middleware
        """
        # Bootstrap backend S
        self._bootstrap_backend_s()

    # ---------------------------- STOP METHODS ------------------------------

    def _switch_backend_s_to_backend_m(
        self,
        ) -> None:
        """
        Prepare to terminate the multiprocessing middleware
        """
        # Stop the old backend
        BackendS.shutdown(self.isFinish, self.backend_s)

        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                "Stopping backend in separate process complete"
            )
        )

        # Bootstrap backend M
        self._bootstrap_backend_m()
        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                "Switching backend from separate to main thread complete"
            )
        )

        # Move to main backend
        self._clean_up_queue()

        self.log(
            LogEntry(
                LogLevelsE.DEBUG.name,
                f"Clean up queue complete, testing if queue is now empty, {self.queue.empty()}"
            )
        )
    
    def _switch_backend_m_to_none(self) -> None:
        # Close up backend in main process
        self.backend_m.finish()
        # Set log method
        self.log = self._log_none
        self._set_current_backend("NONE")

    # ---------------------------- HELP METHODS ------------------------------
    
    def _set_current_backend(self, backend: Backend) -> None:
        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                f"Current backend is switched from {self._current_backend} to {backend}"
                )
        )
        self._current_backend = backend

    def _judge_backend(self, expected: Backend) -> None:
        if self._current_backend != expected:
            self.log(
                LogEntry(
                    LogLevelsE.ERROR.name,
                    f"Invalid backend, current backend {self._current_backend}, expecting {expected}"
                )
            )
            raise Exceptions.UnexpectedBackend

    def _bootstrap_backend_m(self) -> None:
        # Create backend
        self.backend_m = BackendM(
            log_directory=self._directory,
            log_level=self._level,
            write_interval=self._write_interval,
            debug_log_length=self._debug_log_length
        )
        # Change internal log methods
        self.log = self._log_backend_m
        # Change backend flag
        self._set_current_backend("MAIN")
        # Announce it is done
        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                "Create log backend in main process complete"
            )
        )

    def _bootstrap_backend_s(self) -> None:
        # Create the backend
        self.backend_s = BackendS(
            log_directory=self._directory,
            log_level=self._level,
            log_queue=self.queue,
            isFinish=self.isFinish,
            write_interval=self._write_interval,
            debug_log_length=self._debug_log_length,
        )
        # Change internal log methods
        self.log = self._log_backend_s
        # Start multiprocessing
        self.backend_s.start()
        # Change backend flag
        self._set_current_backend("SEPARATE")
        # Announce it is done
        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                "Creating backend in separate process complete"
            )
        )

    def _clean_up_queue(self) -> None:
        """
        This will DEADLOCK if the log method is putting log into queue,
        This method should only be called when the backend is MAIN
        """
        # Make sure it would not deadlock
        self._judge_backend("MAIN")
        # Move queue into logger
        while not self.queue.empty():
            self.log(self.queue.get_nowait())
            self.queue.task_done()

    def _print_logo(self) -> None:
        for line in _logo.split("\n"):
            self.log(LogEntry(
                LogLevelsE.INFO.name,
                line
            ))

    @classmethod
    def _print(cls, log: LogEntry) -> None:
        print(log, end="")