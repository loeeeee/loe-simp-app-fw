# Backend in the main thread
from .model import LogEntry, LogLevels, BackendHelper, ResourceLocator

class Backend(BackendHelper):
    def __init__(
        self, 
        log_directory: ResourceLocator,
        log_level: LogLevels,
        *args, 
        write_interval: float = 5.0,
        debug_log_length: int = 5000,
        **kwargs,
        ) -> None:
        super().__init__(
            log_directory=log_directory,
            log_level=log_level,
            write_interval=write_interval,
            debug_log_length=debug_log_length,
        )
    
    def log(self, log: LogEntry) -> None:
        self.logs.append(log)
        self._write_normal_log()

    def finish(self) -> None:
        self._write_normal_log(noInterval=True)
        self.normal_file_handler.close()
        # self._write_debug_log()
        