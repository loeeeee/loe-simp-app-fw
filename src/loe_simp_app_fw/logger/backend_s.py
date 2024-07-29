# Backend in a separate thread
import multiprocessing
from multiprocessing import JoinableQueue, Process
from multiprocessing.synchronize import Event as EventType
from queue import Empty

from .model import BackendHelper, LogEntry, LogLevels, ResourceLocator, LogLevelsE


class Backend(BackendHelper, Process):
    def __init__(
        self, 
        log_directory: ResourceLocator, 
        log_level: LogLevels, 
        log_queue: JoinableQueue,
        isFinish: EventType,
        *args, 
        write_interval: float = 5.0, 
        debug_log_length: int = 5000, 
        **kwargs
        ) -> None:
        # Init parents
        BackendHelper.__init__(
            self, 
            log_directory, 
            log_level, 
            *args, 
            write_interval=write_interval, 
            debug_log_length=debug_log_length, 
            **kwargs
            )

        Process.__init__(
            self,
            daemon=True,
            name="Logger Backend",
        )

        # Internal variables
        self.finish_flag: EventType = isFinish
        self.queue: JoinableQueue = log_queue

    def run(self) -> None:
        while not self.finish_flag.is_set() and not self.queue.empty():
            self._main()
        self._finish()
        return

    def _main(self) -> None:
        try:
            log = self.queue.get(timeout=self._write_interval)
        except (multiprocessing.TimeoutError, Empty):
            self.logs.append(
                LogEntry(
                    LogLevelsE.DEBUG.name,
                    "A timeout happened because no logs are received"
                )
            )
        else:
            self.logs.append(log)
            self.queue.task_done()

            self._write_normal_log() # This also trims log history to debug log length limit

    def _finish(self) -> None:
        self._write_normal_log(noInterval=True)
        self.normal_file_handler.close()
        self._write_debug_log()