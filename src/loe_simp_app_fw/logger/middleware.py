from multiprocessing import Event, JoinableQueue
from typing import Callable, List
from multiprocessing.synchronize import Event as EventType

from .backend_m import Backend as BackendM
from .backend_s import Backend as BackendS
from .model import Backend, Exceptions, LogEntry, LogLevelsE, ResourceLocator, LogLevels

class Middleware:
    __slots__ = [
        "log", 
        "logs", 
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
        ]

    def __init__(
        self,
        *args,
        **kwargs,
        ) -> None:
        self.log: Callable[[LogEntry], None] = self._log_list

        self.logs: List[LogEntry] = []
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

    def _log_list(self, log: LogEntry) -> None:
        self.logs.append(log)
        self.queue.put(log)
        self._print(log)
        return

    def _log_backend_m(self, log: LogEntry) -> None:
        self.backend_m.log(log)
        # print(f"Manually output: {log}", end="")
        return

    def _log_backend_s(self, log: LogEntry) -> None:
        self.queue.put(log)
        return

    def setup(
        self,
        log_directory: ResourceLocator, 
        log_level: LogLevels, 
        *args, 
        write_interval: float = 5.0, 
        debug_log_length: int = 5000, 
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

        try:
            self._judge_backend("NONE")
        except Exceptions.UnexpectedBackend:
            self.log(
                LogEntry(
                    LogLevelsE.ERROR.name,
                    f"Current backend, {self._current_backend}, is not expected"
                )
            )
            raise
        else:
            self._switch_none_to_backend_s()
        self._isSetUp = True

    def _switch_none_to_backend_s(
        self, 
        ) -> None:
        """
        Bootstrap the middleware
        """
        # Setup the new backend
        self.backend_s = BackendS(
            log_directory=self._directory,
            log_level=self._level,
            log_queue=self.queue,
            isFinish=self.isFinish,
            write_interval=self._write_interval,
            debug_log_length=self._debug_log_length,
        )
        self.log = self._log_backend_s
        # Start multiprocessing backend
        self.backend_s.start()
        self._set_current_backend("SEPARATE")

        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                "Creating backend in separate process complete"
            )
        )

        # Clean instance logs
        self.logs = []

        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                "Clean up instance logs that is in temporary list complete"
            )
        )

    def _switch_backend_s_to_backend_m(
        self,
        ) -> None:
        """
        Prepare to terminate the middleware
        """        
        # Stop the old backend
        self.isFinish.set()
        self.backend_s.join()

        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                "Stopping backend in separate process complete"
            )
        )

        # Setup the new backend
        self.backend_m = BackendM(
            log_directory=self._directory,
            log_level=self._level,
            write_interval=self._write_interval,
            debug_log_length=self._debug_log_length
        )
        self.log = self._log_backend_m

        self._set_current_backend("MAIN")
        
        # Deal with items left in queue
        if self.logs:
            print("Logs is not empty during switch, something terribly wrong happened")
            raise Exceptions.QueueCorruption

        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                "Switching backend to main thread complete"
            )
        )

        while not self.queue.empty():
            self.log(self.queue.get_nowait())
            self.queue.task_done()

        self.log(
            LogEntry(
                LogLevelsE.INFO.name,
                f"Clean up queue complete, testing if queue is now empty, {self.queue.empty()}"
            )
        )
        
        self.queue.join()

    def _switch_backend_m_to_none(self) -> None:
        # Close up backend in main process
        self.backend_m.finish()
        # Set log method
        self.log = self._log_list
        self._set_current_backend("NONE")

    def shutdown(self) -> None:
        # Shutdown sequence: 
        #   Separate backend, main backend, none

        try:
            self._judge_backend("SEPARATE")
        except Exceptions.UnexpectedBackend:
            self.log(
                LogEntry(
                    LogLevelsE.WARNING.name,
                    "No backend in separate process found"
                )
            )
            raise
        else:
            self._switch_backend_s_to_backend_m()
            if self.backend_s.is_alive():
                self.log(
                    LogEntry(
                        LogLevelsE.ERROR.name,
                        "Backend in separate process is still alive"
                    )
                )

        try:
            self._judge_backend("MAIN")
        except Exceptions.UnexpectedBackend:
            self.log(
                LogEntry(
                    LogLevelsE.WARNING.name,
                    "No backend in main process found"
                )
            )
            raise
        else:
            self._switch_backend_m_to_none()
            self.log(
                LogEntry(
                    LogLevelsE.INFO.name,
                    "All file backend shutdown, logs no longer save to file"
                )
            )

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
                    f"Invalid switching backend, current backend {self._current_backend}, expecting {expected}"
                )
            )
            raise Exceptions.UnexpectedBackend
        
    @classmethod
    def _print(cls, log: LogEntry) -> None:
        print(log, end="")