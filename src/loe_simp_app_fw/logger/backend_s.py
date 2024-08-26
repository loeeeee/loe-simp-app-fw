# Backend in a separate thread
from io import TextIOWrapper
import multiprocessing as mp
from multiprocessing.synchronize import Event as EventType
from queue import Empty

from .model import BackendHelper, LogEntry, LogLevels, ResourceLocator, LogLevelsE

mp.set_start_method("fork", force=True) # Spawn is not possible right now

class Backend(BackendHelper, mp.Process):
    def __init__(
        self, 
        log_directory: ResourceLocator, 
        log_level: LogLevels, 
        log_queue: mp.JoinableQueue,
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
            noFileHandler=False, 
            **kwargs
            )

        mp.Process.__init__(
            self,
            name="Logger Backend",
        )

        # Internal variables
        self.finish_flag: EventType = isFinish
        self.queue: mp.JoinableQueue = log_queue

    def run(self) -> None:
        # Create file handler first
        self.debug_file_handler: TextIOWrapper = self._create_debug_file_handler()
        self.normal_file_handler: TextIOWrapper = self._create_normal_file_handler()
        
        # Begin main loop
        try:
            while not self.finish_flag.is_set() or not self.queue.empty():
                self._main(inAHarry=False)
        except KeyboardInterrupt:
            self.logs.append(
                LogEntry(
                    LogLevelsE.INFO.name,
                    "Keyboard interrupt received exiting backend"
                )
            )

        # Clean up and exit
        self._finish()
        return

    def _main(self, inAHarry: bool = False) -> None:
        try:
            log = self.queue.get(block=not inAHarry, timeout=self._write_interval)
        except (mp.TimeoutError, Empty):
            self.logs.append(
                LogEntry(
                    LogLevelsE.DEBUG.name,
                    "A timeout happened because no logs are received"
                )
            )
        else:
            self.logs.append(log)
            self.queue.task_done()

            self._write_normal_log(noInterval=inAHarry) # This also trims log history to debug log length limit

    def _finish(self) -> None:
        while not self.queue.empty():
            self._main(inAHarry=True)
            
        self._write_normal_log(noInterval=True)
        self.normal_file_handler.close()
        self._write_debug_log()

    @staticmethod
    def shutdown(finish_flag: EventType, backend: "Backend") -> None:
        # Set stop flag
        finish_flag.set()
        # Wait for join
        backend.join()
        return